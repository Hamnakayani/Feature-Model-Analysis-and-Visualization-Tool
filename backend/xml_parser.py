import xml.etree.ElementTree as ET
import re

def parse_xml(file_path):
    """
    Parse the XML file to extract features, groups, and constraints with accurate hierarchy details.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        features = {}
        constraints = []

        def parse_feature(node, parent=None, group_type=None):
            """
            Recursively parse features, identifying function features and groups.
            """
            name = node.attrib.get('name')
            if not name:
                return None

            mandatory = node.attrib.get('mandatory', 'false').lower() == 'true'

            # Initialize feature details with a default empty children array
            feature = {
                'parent': parent,
                'mandatory': mandatory,
                'group_type': group_type,
                'children': []
            }

            features[name] = feature  # Add the current feature to features

            # Parse child nodes
            for child in node:
                if child.tag == 'feature':
                    child_name = child.attrib.get('name')
                    if child_name:
                        feature['children'].append(child_name)
                        parse_feature(child, parent=name)
                elif child.tag == 'group':
                    group_type = child.attrib.get('type', 'or').lower()
                    group_features = []
                    for group_child in child:
                        if group_child.tag == 'feature':
                            group_child_name = group_child.attrib.get('name')
                            if group_child_name:
                                group_features.append(group_child_name)
                                parse_feature(group_child, parent=name, group_type=group_type)

                    # Add group as a child with its type and members
                    if group_features:
                        feature['children'].append({
                            'type': 'group',
                            'group_type': group_type,
                            'children': group_features
                        })

            return feature

        # Locate the root feature (assumes the first <feature> is the root)
        root_feature = root.find('.//feature')
        if root_feature is None:
            raise Exception("No root feature found in the XML.")

        # Extract features starting from the root
        parse_feature(root_feature)

        # Parse constraints
        constraints_node = root.find('.//constraints')
        if constraints_node is not None:
            print("Found constraints node") # Debug log
            for constraint in constraints_node.findall('.//constraint'):
                # Handle English constraints
                english = constraint.find('.//englishStatement')
                if english is not None and english.text:
                    print(f"Found English constraint: {english.text.strip()}") # Debug log
                    constraints.append(english.text.strip())
                
                # Handle Boolean constraints
                boolean = constraint.find('.//booleanExpression')
                if boolean is not None and boolean.text:
                    print(f"Found Boolean constraint: {boolean.text.strip()}") # Debug log
                    constraints.append(boolean.text.strip())

        print(f"Total constraints found: {len(constraints)}") # Debug log
        return features, constraints

    except Exception as e:
        print(f"Error parsing XML: {e}") # Debug log
        raise

def convert_boolean_to_boolean_expression(statement):
    """
    Convert Boolean expressions to the correct Boolean format (e.g., "implies" to "→").
    """
    # If the statement contains "implies", treat it as a Boolean expression and convert it
    statement = statement.replace("implies", "→")
    return statement

if __name__ == "__main__":
    try:
        features, constraints = parse_xml("feature-model.xml")  # Replace with your XML file path
        print("\nParsed Features:")
        for feature, details in features.items():
            print(f"{feature}: {details}")
        print("\nParsed Constraints:")
        for constraint in constraints:
            print(constraint)
    except Exception as e:
        print(f"Error parsing XML: {e}")
