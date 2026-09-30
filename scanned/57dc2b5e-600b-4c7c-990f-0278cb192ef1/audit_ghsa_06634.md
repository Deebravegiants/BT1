# [H] datamodel-code-generator vulnerable to arbitrary local file read via XSD `schemaLocation` (`xs:include`/`xs:import`) path traversal, with no remote-ref gate

## Summary
Severity: High
Advisory: GHSA-442q-2j6p-642g
CVE: CVE-2026-55390
CWE: CWE-200, CWE-22, CWE-610
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-442q-2j6p-642g
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.59.0 <0.62.0

## Details
### Summary

When generating models from an XML Schema (`--input-file-type xmlschema`), `datamodel-code-generator` resolves `<xs:include>`, `<xs:import>`, `<xs:redefine>`, and `<xs:override>` `schemaLocation` attributes against the source directory and reads the target with no restriction to the input/base directory. An attacker who controls the input XSD can read arbitrary files via `../` traversal or an absolute path, and the included schema's contents (type names, restrictions, enumerations) are folded into the generated output. Unlike the JSON-Schema `$ref` path, there is no `allow_remote_refs` control for XSD, so `--no-allow-remote-refs` does not mitigate it. This is an unauthenticated path-traversal / information-disclosure issue reachable in the default configuration.

### Details

The XSD parser walks include-style children and reads each `schemaLocation` with only an `is_file()` check (`src/datamodel_code_generator/parser/xmlschema.py`):

```python
location = (source_dir / schema_location).resolve()   # .resolve() collapses ../, escapes base
if location in seen or not location.is_file():
    continue
included_root = self._parse_schema(_read_xml_text(location, self.encoding), location)
```

`schema_location` is attacker-controlled and `_read_xml_text` does `path.read_bytes()`. Because `(source_dir / schema_location).resolve()` normalizes `..` and accepts absolute paths, the resolved target can be any file the process can read; there is no `is_relative_to(base_path)` containment (contrast the JSON-Schema HTTP-local branch, which does enforce it). The same unbounded read occurs both during version detection and during the main include-processing pass, so the included content is incorporated into the generated module.

Related vectors that were tested and do NOT apply (stdlib `xml.etree.ElementTree` is used): external-entity XXE file read does not occur (ElementTree does not fetch external entities), and entity-expansion "billion laughs" is rejected by CPython's expat amplification limit.

### PoC

Self-contained reproducer (creates a temp dir, runs the generator, cleans up): https://gist.github.com/thegr1ffyn/c7096b797926348875d888652867eeb4  (`poc.py`).

Minimal manual reproduction:

```bash
mkdir -p /tmp/x/secret /tmp/x/proj
cat > /tmp/x/secret/leak.xsd <<'EOF'
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:simpleType name="LEAK_5150"><xs:restriction base="xs:string"/></xs:simpleType>
</xs:schema>
EOF
cat > /tmp/x/proj/attack.xsd <<'EOF'
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:include schemaLocation="../../x/secret/leak.xsd"/>
  <xs:element name="Root" type="LEAK_5150"/>
</xs:schema>
EOF
datamodel-codegen --input /tmp/x/proj/attack.xsd --input-file-type xmlschema --no-allow-remote-refs --output /tmp/x/out.py
grep LEAK_5150 /tmp/x/out.py   # content from outside the project dir appears in generated code
```

An absolute `schemaLocation="/abs/path/leak.xsd"` works identically.

### Impact

Arbitrary local file read / path traversal (CWE-22) leading to information disclosure (CWE-200). Any application, CI pipeline, or multi-tenant service that generates models from an attacker-supplied XSD and exposes (returns, logs, commits, renders) the generated code is affected. The attacker can read files outside the input tree whose data is addressable as XSD content (other schemas, configs), and the read itself is an arbitrary-file-access primitive. No flag mitigates it. The attacker controls only the input schema; no authentication or special privileges are required. (Raw bytes of files that are not valid XML are read into the process but not echoed verbatim, since parsing fails; verbatim disclosure applies to XML/XSD-shaped data.)

### Suggested remediation

Reject resolved `schemaLocation` targets that are not `resolved.is_relative_to(self.base_path)`, and bring XSD includes under the same remote/external-reference policy enforced for JSON-Schema `$ref`.

### Maintainer status

Confirmed by maintainer review and regression tests. The private fix PR was merged and released in `0.62.0`: https://github.com/koxudaxi/datamodel-code-generator-ghsa-442q-2j6p-642g/pull/1

Fix summary: reject XSD `schemaLocation` targets that resolve outside the input base path, including relative traversal and absolute paths.

Release status: fixed in `0.62.0`. XML Schema input support was introduced in `0.59.0`, so affected versions are `>= 0.59.0, <= 0.61.0`.

Validation: `uv run --group test --extra http pytest tests/main/xmlschema/test_main_xmlschema.py` passed locally; `uv run --group fix ruff check src/datamodel_code_generator/parser/xmlschema.py tests/main/xmlschema/test_main_xmlschema.py` passed.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-442q-2j6p-642g
- https://github.com/koxudaxi/datamodel-code-generator/commit/d2d5cecd9fd3a2a6dbf148bf0740b83a11fc6820
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.62.0
