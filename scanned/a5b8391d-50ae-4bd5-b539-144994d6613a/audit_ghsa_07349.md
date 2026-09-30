# [H] `datamodel-code-generator` vulnerable to code execution on import via unescaped `validators` entries in --extra-template-data

## Summary
Severity: High
Advisory: GHSA-8m8r-38jm-f355
CVE: CVE-2026-54656
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-8m8r-38jm-f355
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.52.1 <0.60.2

## Details
### Summary

When the Pydantic v2 output mode is in use, `datamodel-code-generator` reads a `validators` array from each model entry in the `--extra-template-data` file and synthesises a Pydantic `@field_validator(...)` decorator from each entry. The field names and the validator mode are interpolated into the decorator call wrapped in *unescaped* single quotes. A value containing `'` breaks out of the string literal, letting an attacker emit an arbitrary positional Python expression into the decorator. The expression is evaluated at class-definition time, i.e. the moment the developer imports the generated module. This is the same trust model as the recently-published GHSA-wjv6-jcfj-mf9r (extras-file comment injection) but the impact is full RCE rather than a docstring leak.

### Details

Sink: `src/datamodel_code_generator/model/pydantic_v2/base_model.py`, `_process_validators` (lines 405–449, at tag `0.60.1` / commit `a321547e`):

```python
def _process_validators(self) -> None:
    validators = self.extra_template_data.get("validators")
    if not validators:
        return
    ...
    for validator in validators:
        fields = validator.get("fields") or [validator.get("field")]
        fields = [f for f in fields if f]
        if not fields:
            continue
        function_path: str = validator["function"]
        function_name = function_path.rsplit(".", 1)[-1]
        mode = validator.get("mode", "after")
        fields_str = ", ".join(f"'{f}'" for f in fields)     # (A) UNESCAPED
        ...
        mode_str = f"mode='{mode}'"                          # (B) UNESCAPED
        prepared_validators.append({
            "fields_str": fields_str,
            "mode_str":   mode_str,
            "method_name": method_name,
            "function_name": function_name,
            "mode": mode,
        })
        self._additional_imports.append(Import.from_full_path(function_path))  # (C)
```

The strings from (A) and (B) flow verbatim into `src/datamodel_code_generator/model/template/pydantic_v2/BaseModel.jinja2`:

```jinja
@field_validator({{ v.fields_str }}, {{ v.mode_str }})
```

There is no `repr()` call, no identifier check, and no quote-escaping.

Secondary sink at (C): `Import.from_full_path(function_path)` splits on the last `.` and emits `from <prefix> import <suffix>`. A `;` in `function_path` therefore lands in the generated import line and runs as a statement at module load.

### PoC

A self-contained one-file PoC is available here: https://gist.github.com/thegr1ffyn/34d5c647e74487ffb2be27c76dace2aa

### Impact

Arbitrary code execution in the developer's interpreter / CI runner the moment the generated module is imported. Anyone who accepts a `--extra-template-data` file from an untrusted source is impacted:

- Pull requests adding or modifying project-local `*.template-data.json` / `.codegen.json` files consumed by a `make codegen` rule or pre-commit hook.
- Configuration snippets pasted from issue templates, READMEs, or third-party guides.
- Multi-tenant CI systems where one tenant's config file is read by another tenant's build.

Same blast radius as GHSA-wjv6-jcfj-mf9r, but silent RCE rather than a docstring leak — significantly higher impact under the same threat model.


 
> Introduced in 0.52.1 by commit [`a2b27562`](https://github.com/koxudaxi/datamodel-code-generator/commit/a2b27562) (*Add --validators option for Pydantic v2 field validators*).

### Resolution

The fix validates `validators` entries with Pydantic models before rendering them. Field names must be valid non-keyword Python identifiers, `function` must be a dotted Python identifier path, and `mode` must be one of Pydantic's supported validator modes. The generated decorator arguments now render field names with `repr()` and mode with `!r`, so validated values are still emitted as Python string literals.

### Remediation

Upgrade to `datamodel-code-generator` `0.60.2` or later.

This issue affects `datamodel-code-generator` versions `>= 0.52.1, <= 0.60.1` and is fixed in `0.60.2`.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-8m8r-38jm-f355
- https://github.com/koxudaxi/datamodel-code-generator/commit/a43d02906111a2fdcaf13ee5b62eb2da85376f19
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.60.2
