# [H] js2py allows remote code execution

## Summary
Severity: High
Advisory: GHSA-h95x-26f3-88hr
CVE: CVE-2024-28397
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-h95x-26f3-88hr
Type: github-advisory

## Affected
- PyPI: `js2py` — affected >=0

## Details
An issue in the component `js2py.disable_pyimport()` of js2py up to v0.74 allows attackers to execute arbitrary code via a crafted API call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28397
- https://github.com/PiotrDabkowski/Js2Py/pull/323
- https://github.com/Marven11
- https://github.com/Marven11/CVE-2024-28397-js2py-Sandbox-Escape
- https://github.com/PiotrDabkowski/Js2Py
