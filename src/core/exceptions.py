
class ComponentError(Exception): pass
class ContainerError(ComponentError): pass
class FieldValidationError(ValueError): pass
class SchemaValidationError(TypeError): pass