def translate_to_logic(features, constraints):
    """
    Translate features into propositional logic and combine with constraints.
    """
    logic_formula = []
    processed_relationships = set()
    processed_features = set()

    def add_relationship(relationship):
        if relationship not in processed_relationships:
            logic_formula.append(relationship)
            processed_relationships.add(relationship)

    def handle_feature(feature_name, feature_details):
        if feature_name in processed_features:
            return
        processed_features.add(feature_name)

        # Handle parent-child relationships
        if feature_details['parent']:
            parent = feature_details['parent']
            if feature_details['mandatory']:
                add_relationship(f"({parent} → {feature_name})")
                add_relationship(f"({feature_name} → {parent})")
            else:
                add_relationship(f"({parent} ↔ ({feature_name} ∨ ~{feature_name}))")

        # Handle children
        for child in feature_details['children']:
            if isinstance(child, str):
                handle_feature(child, features[child])
            elif isinstance(child, dict):
                group_type = child.get('group_type', 'or')
                group_children = child.get('children', [])

                if group_type == 'xor':
                    xor_clauses = [
                        f"({c1} ∧ {' ∧ '.join([f'~{c2}' for c2 in group_children if c1 != c2])})"
                        for c1 in group_children
                    ]
                    xor_logic = " ∨ ".join(xor_clauses)
                    add_relationship(f"({feature_name} → ({xor_logic}))")
                    for c in group_children:
                        add_relationship(f"({c} → {feature_name})")

                elif group_type == 'or':
                    or_logic = " ∨ ".join(group_children)
                    add_relationship(f"({feature_name} → ({or_logic}))")
                    for c in group_children:
                        add_relationship(f"({c} → {feature_name})")

    # Add root feature
    root_feature = next(f for f, details in features.items() if details['parent'] is None)
    logic_formula.append(root_feature)

    # Process all features
    for feature_name, feature_details in features.items():
        handle_feature(feature_name, feature_details)

    # Add translated constraints at the end
    for constraint in constraints:
        # If constraint is already in propositional logic format, add directly
        if any(op in constraint for op in ['→', '↔', '∧', '∨', '~']):
            add_relationship(constraint)
        else:
            # Translate English constraints
            translated = translate_constraint(constraint, features)
            if translated:
                add_relationship(translated)

    # Combine all formulas with AND (∧)
    final_formula = " ∧ ".join(logic_formula)
    return final_formula

def translate_constraint(statement, features):
    """Translate English constraints into Boolean logic."""
    statement = statement.strip().rstrip('.')
    
    if "is required to" in statement:
        parts = statement.split("is required to")
        if len(parts) == 2:
            left = parts[0].strip().replace("The", "").replace("feature", "").strip()
            right_part = parts[1].strip().replace("filter the catalog by", "").strip()
            right = f"By{right_part[0].upper()}{right_part[1:]}"
            return f"({left} → {right})"
            
    if "requires" in statement:
        parts = statement.split("requires")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            return f"({left} → {right})"
            
    if "excludes" in statement:
        parts = statement.split("excludes")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            return f"~({left} ∧ {right})"
            
    return None
