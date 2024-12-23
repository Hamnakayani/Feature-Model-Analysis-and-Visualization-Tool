import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from xml_parser import parse_xml
from logic_translator import translate_to_logic
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle the upload of an XML file, parse it, and return the parsed features.
    """
    if 'file' not in request.files:
        app.logger.error("No file part in the request.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("No selected file.")
        return jsonify({"error": "No selected file"}), 400

    # Validate file extension
    if not file.filename.lower().endswith('.xml'):
        app.logger.error("Invalid file format. Only XML files are allowed.")
        return jsonify({"error": "Invalid file format. Only XML files are allowed."}), 400

    # Save the file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(file_path)
        app.logger.info(f"File saved at: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found after saving: {file_path}")

        # Parse the XML file
        features, constraints = parse_xml(file_path)
        app.logger.info(f"Parsed features: {features}")
        app.logger.info(f"Parsed constraints: {constraints}")

        # Return parsed data to frontend
        return jsonify({"features": features, "constraints": constraints})

    except ET.ParseError as e:
        app.logger.error(f"XML Parsing error: {e}")
        return jsonify({"error": f"XML Parsing error: {e}"}), 400

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
            app.logger.info(f"Temporary file deleted: {file_path}")

@app.route('/translate', methods=['POST'])
def translate_logic():
    """
    Translate parsed features into propositional logic.
    """
    data = request.get_json()
    features = data.get("features")
    constraints = data.get("constraints", [])

    try:
        logic_formula = translate_to_logic(features, constraints)
        return jsonify({"logic": logic_formula})

    except Exception as e:
        app.logger.error(f"Logic translation error: {e}")
        return jsonify({"error": f"Logic translation error: {e}"}), 500

@app.route('/visualize', methods=['POST'])
def visualize_feature_model():
    """
    Return the hierarchical structure of the feature model for visualization.
    """
    data = request.get_json()
    features = data.get("features")

    if not features:
        return jsonify({"error": "No features provided"}), 400

    try:
       
        hierarchy = build_feature_hierarchy(features)  
        return jsonify({"hierarchy": hierarchy})

    except Exception as e:
        app.logger.error(f"Visualization error: {e}")
        return jsonify({"error": f"Visualization error: {e}"}), 500

@app.route('/mwp', methods=['POST'])
def calculate_mwp():
    """
    Calculate the Minimum Working Products (MWPs) based on the uploaded XML.
    """
    data = request.get_json()
    features = data.get("features")
    constraints = data.get("constraints")

    try:
        from mwp_calculator import identify_mwp
        mwps = identify_mwp(features, constraints)
        return jsonify({"mwp": mwps})
    except Exception as e:
        app.logger.error(f"MWP calculation error: {e}")
        return jsonify({"error": f"MWP calculation error: {e}"}), 500


def build_feature_hierarchy(features):
    """
    Helper function to build a feature hierarchy.
    """
    hierarchy = []

    # Identify the root feature (the one with no parent)
    root_feature = next(f for f, details in features.items() if details['parent'] is None)
    
    def add_children(feature_name):
        feature = features.get(feature_name)
        if not feature:
            return None

        # Build the current feature node
        node = {
            'name': feature_name,
            'mandatory': feature['mandatory'],
            'children': []
        }

        # Recursively add children if they exist
        for child in feature['children']:
            if isinstance(child, str):  # Direct child
                child_node = add_children(child)
                if child_node:
                    node['children'].append(child_node)
            elif isinstance(child, dict):  # Grouped child
                group_node = {
                    'type': child['group_type'],
                    'children': [add_children(group_child) for group_child in child['children']]
                }
                node['children'].append(group_node)

        return node

    # Start building from the root feature
    hierarchy.append(add_children(root_feature))

    return hierarchy


if __name__ == "__main__":
    app.run(debug=True)
