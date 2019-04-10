from ruamel.yaml.comments import TaggedScalar


def replace_references(template, old_reference, new_reference):
    """
    replaces CloudFormation references { "Ref": old_reference } with { "Ref": new_reference } in `template`.
    """
    if isinstance(template, dict):
        for name, value in template.items():
            if name == 'Ref' and value == old_reference:
                template['Ref'] = new_reference
            elif isinstance(value, TaggedScalar) and value.tag and value.tag.value == '!Ref' and value.value == old_reference:
                value.value = new_reference
            else:
                replace_references(template[name], old_reference, new_reference)
    elif isinstance(template, list):
        for i, value in enumerate(template):
            replace_references(value, old_reference, new_reference)
    else:
        pass  # a primitive, no recursive required.
