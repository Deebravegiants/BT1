# [H] openapi-python-client Arbitrary Code Generation vulnerability

## Summary
Severity: High
Advisory: GHSA-9x4c-63pf-525f
CVE: CVE-2020-15142
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-20
Source: https://github.com/advisories/GHSA-9x4c-63pf-525f
Type: github-advisory

## Affected
- PyPI: `openapi-python-client` — affected >=0 <0.5.3

## Details
### Impact
Clients generated with a maliciously crafted OpenAPI Document can generate arbitrary Python code. Subsequent execution of this malicious client is arbitrary code execution.

Giving this a CVSS of 8.0 (high) with CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H/E:P/RL:U/RC:C .

### Patches
Fix will be included in version 0.5.3

### Workarounds
Inspect OpenAPI documents before generating, or inspect generated code before executing.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [openapi-python-client](https://github.com/triaxtec/openapi-python-client/issues)
* Email us at [danthony@triaxtec.com](mailto:danthony@triaxtec.com)

## References
- https://github.com/triaxtec/openapi-python-client/security/advisories/GHSA-9x4c-63pf-525f
- https://nvd.nist.gov/vuln/detail/CVE-2020-15142
- https://github.com/openapi-generators/openapi-python-client/commit/f7a56aae32cba823a77a84a1f10400799b19c19a
- https://github.com/triaxtec/openapi-python-client/commit/f7a56aae32cba823a77a84a1f10400799b19c19a
- https://github.com/openapi-generators/openapi-python-client
- https://github.com/openapi-generators/openapi-python-client/releases/tag/v.0.5.3
- https://github.com/pypa/advisory-database/tree/main/vulns/openapi-python-client/PYSEC-2020-71.yaml
- https://github.com/triaxtec/openapi-python-client/blob/main/CHANGELOG.md#053---2020-08-13
- https://pypi.org/project/openapi-python-client
