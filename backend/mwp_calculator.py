from itertools import product

def generate_all_mwps(features, constraints):
    """
    Generate all possible MWPs, prioritizing XOR children based on constraints.
    """
    def process_feature(feature):
        """
        Recursively process a feature and generate combinations for groups (XOR, OR).
        """
        result = [[feature]]  # Start with the feature itself
        children = features[feature].get('children', [])

        for child in children:
            if isinstance(child, str):  # A direct child feature
                if features[child]['mandatory']:
                    # Mandatory child must be included
                    child_combinations = process_feature(child)
                    result = [r + c for r in result for c in child_combinations]
            elif isinstance(child, dict):  # Group type (XOR/OR)
                group_type = child.get('group_type')
                group_children = child['children']

                if group_type == 'xor':
                    # XOR: Prioritize the constrained child, if any
                    constrained_child = find_constrained_child(group_children, constraints)
                    if constrained_child:
                        group_combinations = process_feature(constrained_child)
                    else:
                        # Default to the first child if no constraints match
                        group_combinations = process_feature(group_children[0])
                    result = [r + gc for r in result for gc in group_combinations]

                elif group_type == 'or':
                    # OR: Include all combinations of children
                    group_combinations = []
                    for i in range(1, len(group_children) + 1):
                        for combo in product(*[process_feature(gc) for gc in group_children[:i]]):
                            group_combinations.append([item for sublist in combo for item in sublist])
                    result = [r + gc for r in result for gc in group_combinations]

        return result

    root = list(features.keys())[0]
    return process_feature(root)


def find_constrained_child(group_children, constraints):
    """
    Identify if any child in the XOR group appears in the constraints.
    """
    for constraint in constraints:
        if "→" in constraint:
            left, _ = constraint.split("→")
            left = left.strip()
            if left in group_children:
                return left
    return None  # No constrained child found


def apply_constraints(mwps, features, constraints):
    """
    Apply constraints to filter valid MWPs.
    """
    valid_mwps = []

    for mwp in mwps:
        valid = True
        for constraint in constraints:
            if "→" in constraint:
                left, right = constraint.split("→")
                left = left.strip().strip('()')
                right = right.strip().strip('()')

                # If left feature is present, right feature must also be present
                if left in mwp and right not in mwp:
                    valid = False
                    break

                # For ByLocation constraint, ensure Location feature is included
                if right.startswith('By') and right in mwp:
                    base_feature = right[2:]  # Remove 'By' prefix
                    if base_feature not in mwp:
                        valid = False
                        break

        if valid:
            valid_mwps.append(mwp)

    return valid_mwps


def identify_mwp(features, constraints):
    """
    Identify all valid MWPs by generating possible combinations and applying constraints.
    """
    try:
        # Step 1: Generate all MWPs
        all_mwps = generate_all_mwps(features, constraints)

        # Step 2: Apply constraints to filter out invalid MWPs
        valid_mwps = apply_constraints(all_mwps, features, constraints)

        # Step 3: Find the minimum size among valid MWPs
        if valid_mwps:
            min_size = min(len(mwp) for mwp in valid_mwps)
            # Return all MWPs that have the minimum size
            minimal_mwps = [mwp for mwp in valid_mwps if len(mwp) == min_size]
            return minimal_mwps

        return []  # No valid configuration found

    except Exception as e:
        print(f"Error identifying MWPs: {e}")
        raise RuntimeError(f"Error identifying MWPs: {e}")
     

