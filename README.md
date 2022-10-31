# MVCE for NameError: Could not de-stringify annotation UUID

```python
Traceback (most recent call last):
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/util/typing.py", line 118, in de_stringify_annotation
    annotation = eval(annotation, base_globals, None)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
NameError: name 'UUID' is not defined

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/peter/PycharmProjects/sqla-test/main.py", line 1, in <module>
    from lib.domain import Author
  File "/home/peter/PycharmProjects/sqla-test/lib/domain.py", line 6, in <module>
    class Author(Base):
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/decl_api.py", line 701, in __init_subclass__
    _as_declarative(cls._sa_registry, cls, cls.__dict__)
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/decl_base.py", line 207, in _as_declarative
    return _MapperConfig.setup_mapping(registry, cls, dict_, None, {})
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/decl_base.py", line 288, in setup_mapping
    return _ClassScanMapperConfig(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/decl_base.py", line 523, in __init__
    self._extract_mappable_attributes()
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/decl_base.py", line 1278, in _extract_mappable_attributes
    value.declarative_scan(
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/properties.py", line 660, in declarative_scan
    self._init_column_for_annotation(
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/orm/properties.py", line 686, in _init_column_for_annotation
    argument = de_stringify_annotation(cls, argument)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/peter/PycharmProjects/sqla-test/.venv/lib/python3.11/site-packages/sqlalchemy/util/typing.py", line 120, in de_stringify_annotation
    raise NameError(
NameError: Could not de-stringify annotation UUID
```

```python
# sqlalchemy/util/typing.py

def de_stringify_annotation(
    cls: Type[Any],
    annotation: _AnnotationScanType,
    str_cleanup_fn: Optional[Callable[[str], str]] = None,
) -> Type[Any]:
    ...
    if (
        is_fwd_ref(annotation)
        and not cast(ForwardRef, annotation).__forward_evaluated__
    ):
        annotation = cast(ForwardRef, annotation).__forward_arg__

    if isinstance(annotation, str):
        if str_cleanup_fn:
            annotation = str_cleanup_fn(annotation)

        # HERE: UUID doesn't exist in `lib.domain` globals, rather `lib.orm` globals.
        base_globals: "Dict[str, Any]" = getattr(
            sys.modules.get(cls.__module__, None), "__dict__", {}
        )

        try:
            annotation = eval(annotation, base_globals, None)
        except NameError as err:
            raise NameError(
                f"Could not de-stringify annotation {annotation}"
            ) from err
    return annotation  # type: ignore
```

Fixes my local case, haven't run against tests though:

```python
def de_stringify_annotation(
    cls: Type[Any],
    annotation: _AnnotationScanType,
    str_cleanup_fn: Optional[Callable[[str], str]] = None,
) -> Type[Any]:
    ...
    if (
        is_fwd_ref(annotation)
        and not cast(ForwardRef, annotation).__forward_evaluated__
    ):
        annotation = cast(ForwardRef, annotation).__forward_arg__

    if isinstance(annotation, str):
        if str_cleanup_fn:
            annotation = str_cleanup_fn(annotation)

        # A different approach, works in this case but not correct. A name in MRO module may be 
        # repeated with a different type, overwriting globals with type incorrect relative to cls.
        # Perhaps if the name of the attribute that owns the annotation was available here, we 
        # could check that it exists in `annotations` and know that this is the module needed to 
        # find the type.
        base_globals: "Dict[str, Any]" = {}
        for cl in cls.mro():
            annotations = getattr(cl, "__annotations__", {})
            if not annotations:
                continue
            module = sys.modules.get(cl.__module__, None)
            module_globals = getattr(module, "__dict__", {})
            base_globals.update(module_globals)

        try:
            annotation = eval(annotation, base_globals, None)
        except NameError as err:
            raise NameError(
                f"Could not de-stringify annotation {annotation}"
            ) from err
    return annotation  # type: ignore
```
