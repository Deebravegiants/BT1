# [H] `datamodel-code-generator` vulnerable to code injection via unescaped carriage return in `--extra-template-data` `comment` field

## Summary
Severity: High
Advisory: GHSA-wjv6-jcfj-mf9r
CVE: CVE-2026-54654
CWE: CWE-1336, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-wjv6-jcfj-mf9r
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.14.1 <0.60.2

## Details
### Summary

`datamodel-code-generator` is vulnerable to code injection when a developer passes an `--extra-template-data` file whose `comment` value contains a literal `\r` (carriage return). The `comment` variable is rendered into a Python `#` comment in six built-in templates with **no** line-terminator escaping. Python's tokenizer treats a bare CR as a physical-line terminator (see [Python language reference — Physical lines](https://docs.python.org/3/reference/lexical_analysis.html#physical-lines)), so the comment ends at the `\r` and the text after it is parsed as Python, including, when the CR is followed by suitable indentation, as a statement within the class body that follows on the next template line.

### Details

The vulnerable templates each contain `# {{ comment }}` with no escaping:

- `src/datamodel_code_generator/model/template/TypeAliasAnnotation.jinja2:12` and `:19`
- `src/datamodel_code_generator/model/template/TypeAliasType.jinja2:12` and `:19`
- `src/datamodel_code_generator/model/template/TypeStatement.jinja2:12` and `:19`
- `src/datamodel_code_generator/model/template/pydantic_v2/BaseModel.jinja2:4`
- `src/datamodel_code_generator/model/template/pydantic_v2/RootModel.jinja2:19`
- `src/datamodel_code_generator/model/template/pydantic_v2/RootModelTypeAlias.jinja2:13`

The `pydantic_v2/BaseModel.jinja2:4` site is representative:

```jinja2
class {{ class_name }}({{ base_class }}):{% if comment is defined %}  # {{ comment }}{% endif %}
```

When the developer-supplied extras file populates `comment` for a model, the value reaches the template via `DataModel.extra_template_data` (set in `src/datamodel_code_generator/model/base.py:736-742`) and Jinja2 interpolates it raw. None of the templates use `comment_safe`, `escape_docstring`, or any other line-terminator filter.

### PoC
Complete self contained POC is available at my secret gist: https://gist.github.com/thegr1ffyn/8ad6b8cb3cc2be9d3a0144aeb6896a3f

### Impact

- **Who's affected**: any developer or CI pipeline that runs `datamodel-codegen --extra-template-data <file>` where the extras file is influenced by attacker-controlled input. Realistic scenarios include:
  - Extras file generated from a third-party schema-annotation system.
  - Extras file vendored from an upstream repository.
  - Extras file produced by a script that merges multiple `comment` sources.
  - Build pipelines that template the extras file from environment variables, ticket descriptions, or commit metadata.
- **What it gains**: arbitrary Python code execution in the importer's process at `import` time.
- **What it does NOT need**: the schema itself can be entirely benign; only the extras file needs to contain the malicious `comment`.
- **What does block it**: not passing `--extra-template-data`, or rejecting extras files whose `comment` values contain `\r`, `\x0b`, or `\x0c` before invocation.

### Resolution

The fix normalizes `comment` values from built-in `--extra-template-data` before template rendering. Inline comments now convert CRLF, bare CR, vertical tab, and form feed into LF and prefix continuation lines with `# `, so attacker-controlled text stays inside the generated Python comment block.

### Remediation

Upgrade to `datamodel-code-generator` `0.60.2` or later.

This issue affects `datamodel-code-generator` versions `>= 0.14.1, <= 0.60.1` and is fixed in `0.60.2`.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-wjv6-jcfj-mf9r
- https://github.com/koxudaxi/datamodel-code-generator/commit/b73abb5cd703a50471b8950bbd3bd0b82ad71de7
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.60.2
