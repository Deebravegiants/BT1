# [H] `datamodel-code-generator` vulnerable to code injection in via attacker-controlled `default_factory` schema field

## Summary
Severity: High
Advisory: GHSA-386q-5hp3-95m9
CVE: CVE-2026-54653
CWE: CWE-1336, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-386q-5hp3-95m9
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.17.0 <0.60.2

## Details
### Summary

`datamodel-code-generator` is vulnerable to code injection when generating Python models from an attacker-controlled JSON Schema, OpenAPI, YAML, JSON, Avro, Protobuf, or XSD schema. When a property carries a `"default_factory"` key, its value is interpolated verbatim — as a raw Python expression — into the generated `Field(default_factory=...)` / `field(default_factory=...)` call. Because this assignment is evaluated at class-definition time (i.e. on `import` of the generated module), an attacker who controls the schema controls a Python expression that runs in the consumer's process. No special CLI flags are required.

### Details

The vulnerable chain spans the JSON-Schema-shaped parser and three sink locations (Pydantic v2, dataclass, msgspec):

**Source — schema → `extras`**:

- `src/datamodel_code_generator/parser/jsonschema.py:600-614` — `DEFAULT_FIELD_KEYS` includes the literal string `"default_factory"`.
- `src/datamodel_code_generator/parser/jsonschema.py:457-459` — `JsonSchemaObject.__init__` stores any non-standard key (including `default_factory`) in `self.extras`.
- `src/datamodel_code_generator/parser/jsonschema.py:797-812` — `get_field_extras` preserves `default_factory` through to the field model.

**Sinks — `extras` → generated Python expression**:

1. `src/datamodel_code_generator/model/pydantic_base.py:222-249`:

   ```python
   default_factory = data.pop("default_factory", None)
   ...
   if default_factory is not None:
       field_arguments = [f"default_factory={default_factory}", *field_arguments]
   ```

   The `default_factory` value is interpolated raw (no `repr()`, no validation).

2. `src/datamodel_code_generator/model/dataclass.py:211`:

   ```python
   f"{k}={v if k == 'default_factory' else repr(v)}"
   ```

   Explicit special-case to skip `repr()` for `default_factory`.

3. `src/datamodel_code_generator/model/msgspec.py:361` — same pattern as dataclass.

Because `default_factory` is in `DEFAULT_FIELD_KEYS`, no special CLI flag is needed to reach the sink. Any input format that uses the JSON-Schema-shaped parser (`jsonschema`, `openapi`, `yaml`, `json`, `dict`, `csv`) — and any input format that converts to it (`avro`, `protobuf`, `xmlschema`) — is in scope.

### Confirmed PoC matrix

| Input file type | Output model type | Result |
|---|---|---|
| `jsonschema` | `pydantic_v2.BaseModel` | RCE on import |
| `jsonschema` | `dataclasses.dataclass` | RCE on import |
| `jsonschema` | `msgspec.Struct` | RCE on import |
| `jsonschema` | `typing.TypedDict` | safe (TypedDict doesn't render `field()`; `default_factory` silently dropped) |
| `openapi`    | `pydantic_v2.BaseModel` | RCE on import |

Other JSON-Schema-shaped inputs (`yaml`, `json`, `dict`, `csv`, `avro`, `protobuf`, `xmlschema`) follow the same code path and are expected to reproduce.

### PoC
Self contained Proof of Concept is available at my secret gist: https://gist.github.com/thegr1ffyn/9648b0fe4fcf7d569ac8e61dd11eebaf

### Impact

- **Who's affected**: any developer or CI pipeline that runs `datamodel-codegen` against a schema they didn't author themselves — third-party API specs, schemas pulled from a registry, vendored upstream `.json` / `.yaml` / `.avsc` / `.proto` / `.xsd` files, schemas fetched from a remote URL or introspection endpoint — *and* who imports the generated `.py`.
- **What it gains**: arbitrary Python code execution in the importer's process at `import` time. The PoC copies `/etc/passwd` to a tmp file to demonstrate arbitrary read; the same primitive supports any operation the importing process can perform (filesystem write, environment exfiltration, secondary network calls, RCE on CI runners).
- **What it does NOT need**: no special CLI flags, no custom templates, no `--extra-template-data`, no `--use-schema-description`. Default invocation against a malicious schema is sufficient.
- **What does block it**: choosing `--output-model-type typing.TypedDict` (which doesn't render `field()` / `Field()` calls). All other supported output model types are vulnerable.

### Resolution

The fix validates schema-provided `default_factory` values while extracting JSON Schema field extras. Only the supported factory names `dict`, `list`, and `set` are accepted; any other value now raises a generator error before code generation. Generator-created default factories for supported mutable defaults and optional nested models continue to use the existing code paths.

### Remediation

Upgrade to `datamodel-code-generator` `0.60.2` or later.

This issue affects `datamodel-code-generator` versions `>= 0.17.0, <= 0.60.1` and is fixed in `0.60.2`.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-386q-5hp3-95m9
- https://github.com/koxudaxi/datamodel-code-generator/commit/17fc235e234cbcfaaadef8c74cb72c9687db0d1d
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.60.2
