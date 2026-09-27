# [H] `datamodel-code-generator` vulnerable to code execution on import via `x-python-type` JSON-Schema extension in datamodel-code-generator

## Summary
Severity: High
Advisory: GHSA-m34r-v34r-rf9q
CVE: CVE-2026-54655
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-m34r-v34r-rf9q
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.51.0 <0.60.2

## Details
### Summary
`datamodel-code-generator` honours a custom `x-python-type` JSON-Schema extension that lets a schema author override the generated Python type for a field. The value is forwarded verbatim into the generated Python source as the field annotation, with a single sanitisation pass that is trivial to bypass. An attacker who controls a JSON Schema fed to `datamodel-codegen` can therefore embed an arbitrary Python statement in the generated module, which executes at class-definition time the moment the developer imports the file. No `--extra-template-data` and no special flags are required; the vulnerable code is reachable with default settings.

### Details
Sink: `src/datamodel_code_generator/parser/jsonschema.py`, `_get_python_type_override` (lines 2055–2096, at tag `0.60.1` / commit `a321547e`):

```python
def _get_python_type_override(self, obj: JsonSchemaObject) -> DataType | None:
    x_python_type = obj.extras.get("x-python-type")
    if not x_python_type or not isinstance(x_python_type, str):
        return None
    schema_type = obj.type if isinstance(obj.type, str) else None
    if self._is_compatible_python_type(schema_type, x_python_type):
        return None
    base_type = self._get_python_type_base(x_python_type)
    import_ = self._resolve_type_import(base_type)
    type_str = x_python_type
    prefix = x_python_type.split("[", maxsplit=1)[0]
    if "." in prefix:                                  # only sanitiser
        type_str = base_type + x_python_type[len(prefix):]
        ...
    ...
    result = self.data_type(type=type_str, import_=import_)
    ...
    return result
```

`DataType.type` flows unescaped into `{{ field.type_hint }}` in every model template
(`model/template/pydantic_v2/BaseModel.jinja2`,
`model/template/dataclass.jinja2`,
`model/template/TypedDictClass.jinja2`,
`model/template/msgspec.jinja2`, …).

The only sanitiser — the dot-rewrite at the marked line — fires only when `.` is in the substring **before the first `[`** in the value. Placing `[` early (e.g. `X[1]; <payload>`) keeps `prefix == "X"` so the rewrite is skipped and the whole value lands in the generated annotation.

`from __future__ import annotations` (emitted by default) makes the `X[1]` portion a lazy string, so `X` does not need to resolve at runtime. Everything after `;` is parsed as a real statement in the class body and is executed when the class is constructed during `import`.

Output-model types confirmed vulnerable in testing: `pydantic_v2.BaseModel`, `dataclasses.dataclass`, `typing.TypedDict`. `msgspec.Struct` emits structurally identical code.

### PoC
A self-contained PoC is available at: https://gist.github.com/thegr1ffyn/1a7ff2561a581074c49785230b2c5700

### Impact
Arbitrary code execution in the developer's interpreter / CI runner as soon as the generated module is imported. Reachable from any workflow that ingests an untrusted JSON Schema:

- OpenAPI / JSON-Schema documents fetched from third-party services or public registries.
- Customer-supplied schemas in B2B platforms that auto-generate client SDKs from user input.
- Schema files added by a malicious commit in a polyglot repository that triggers CI code generation.

The compromise is silent: the schema is valid JSON, the generator emits syntactically clean Python (the trojan statement is a single indented line in the class body), and only the *use* of the generated file triggers the payload.

Anyone running `datamodel-codegen` against an attacker-supplied schema is impacted. CI runners and developer workstations are the primary blast radius.

### Resolution

The fix validates `x-python-type` before constructing the generated type annotation. The value is parsed with `ast.parse(..., mode="eval")` and accepted only when the AST is shaped like a Python type annotation, including names, attributes, subscripts, tuple/list annotation arguments, `|` unions, and safe literal values where annotation syntax allows them. Statements, calls, and other executable expressions are rejected before code generation. The validator is cached to avoid repeated AST parsing for repeated values.

### Remediation

Upgrade to `datamodel-code-generator` `0.60.2` or later.

This issue affects `datamodel-code-generator` versions `>= 0.51.0, <= 0.60.1` and is fixed in `0.60.2`.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-m34r-v34r-rf9q
- https://github.com/koxudaxi/datamodel-code-generator/commit/2c93c9b712f43391dcfa975a1e4aa0b7c93ccbba
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.60.2
