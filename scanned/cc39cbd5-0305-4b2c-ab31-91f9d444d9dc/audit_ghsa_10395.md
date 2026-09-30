# [M] Giskard has Unsandboxed Jinja2 Template Rendering in ConformityCheck

## Summary
Severity: Medium
Advisory: GHSA-7xjm-g8f4-rp26
CVE: CVE-2026-40320
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-7xjm-g8f4-rp26
Type: github-advisory

## Affected
- PyPI: `giskard-checks` — affected >=0 <1.0.2b1

## Details
## Summary
 
The `ConformityCheck` class in `giskard-checks` rendered the `rule` parameter through Jinja2's default `Template()` constructor. Because the `rule` string is silently interpreted as a Jinja2 template, a developer may not realize that template expressions embedded in rule definitions are evaluated at runtime. In a scenario where check definitions are loaded from an untrusted source (e.g. a shared project file or externally contributed configuration), this could lead to arbitrary code execution.

`giskard-checks` is a local developer testing library with no network-facing service. Check definitions, including the `rule` parameter, are provided in application code or project configuration files and executed locally. Exploitation requires write access to a check definition and subsequent execution of the test suite by a developer.

However, the implicit template evaluation of the `rule` parameter is not obvious from the API surface. This hidden behavior increases the likelihood of a developer inadvertently passing untrusted input to it when integrating the library into a larger system. 

## Affected Component
 
`conformity.py`, line 59:
```python
from jinja2 import Template
...
formatted_rule = Template(self.rule).render(trace=trace)
```
 
## Affected Versions
 
`giskard-checks` < 1.0.2b1
 
## Patched Version
 
`giskard-checks` >= **1.0.2b1** (template parsing removed from rule evaluation entirely)
 
## Remediation
 
Upgrade to `giskard-checks` >= 1.0.2b1. The template rendering has been removed from rule evaluation.
 
## Credit
 
Giskard-AI thanks @dhabaleshwar for identifying the unsandboxed template usage.

## References
- https://github.com/Giskard-AI/giskard-oss/security/advisories/GHSA-7xjm-g8f4-rp26
- https://nvd.nist.gov/vuln/detail/CVE-2026-40320
- https://github.com/Giskard-AI/giskard-oss
- https://github.com/Giskard-AI/giskard-oss/releases/tag/giskard-checks%2Fv1.0.2b1
