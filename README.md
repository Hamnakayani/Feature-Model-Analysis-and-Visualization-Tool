# Feature Model Analysis and Visualization Tool

## Overview
This tool is designed to assist in software product line engineering by analyzing and visualizing feature models. Feature models represent hierarchical relationships and constraints of system features. The tool supports XML input for feature models, translates them into propositional logic, identifies Minimum Working Products (MWPs), and provides an interactive visualization to verify feature selections against constraints.

## Features
### 1. XML Parsing and Input Handling
- Accepts XML files representing the feature model.
- Supports hierarchical relationships (mandatory, optional, XOR, OR) and cross-tree constraints (e.g., requires, excludes).
- Validates XML files against a predefined schema (XSD).

### 2. Translation to Propositional Logic
- Parses the feature model and converts it into propositional logic.
- Supports translations for various relationships:
  - **Root:** `B` (if B is the root).
  - **Mandatory Feature:** `B → A` (if B has a mandatory child A).
  - **Optional Feature:** `B ↔ (A ∨ ¬A)` (if A is optional under B).
  - **OR Group:** `(A ∨ B)` (any combination of features in an OR group can be selected).
  - **XOR Group:** `(A ∧ ¬B) ∨ (B ∧ ¬A)` (only one feature in an XOR group can be selected).
  - Cross-tree constraints are translated from English or propositional logic.

### 3. Minimum Working Product (MWP) Identification
- Computes and displays a minimal valid configuration of features satisfying all mandatory constraints while minimizing optional features and ensuring cross-tree constraints.

### 4. Feature Model Visualization and Interaction
- Visualizes the feature model as an interactive checkbox tree:
  - Mandatory and optional features are visually distinguished.
  - XOR group features automatically disable others in the group when selected.
  - Dynamically validates selections based on constraints.

### 5. Feature Selection Verification
- Verifies if the user-selected configuration is valid.
- Provides detailed error messages for invalid configurations, such as unmet mandatory features or violated constraints.

### 6. Cross-Tree Constraints Handling
- Supports cross-tree constraints (e.g., "A requires B" or "A excludes B").
- Translates English constraints into propositional logic with user prompts for confirmation or input.

## Technologies Used
- **Backend:** Python (Flask/Django)
  - **SAT Solver:** PySAT
- **Frontend:** React.js
- **Others:**
  - XML parsing libraries (e.g., `xml.etree.ElementTree` or `lxml` in Python).
  - CSS for styling.

## Installation

### Prerequisites
- Python 3.x
- Node.js and npm/yarn

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Hamnakayani/Feature-Model-Analysis-and-Visualization-Tool.git
   cd Feature-Model-Analysis-and-Visualization-Tool
   ```

2. **Backend Setup:**
   - Navigate to the backend directory:
     ```bash
     cd backend
     ```
   - Create and activate a virtual environment (optional):
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the backend server:
     ```bash
     python app.py  # Or the main file of your backend
     ```

3. **Frontend Setup:**
   - Navigate to the frontend directory:
     ```bash
     cd ../frontend
     ```
   - Install dependencies:
     ```bash
     npm install
     ```
   - Start the frontend development server:
     ```bash
     npm start
     ```

4. **Access the Application:**
   - Open your browser and navigate to `http://localhost:3000` for the frontend.

## Usage
1. Upload an XML file representing the feature model.
2. View the translated propositional logic formula.
3. Explore the interactive checkbox tree for feature selection.
4. Verify the selected configuration for feasibility.
5. View and resolve cross-tree constraints as needed.


