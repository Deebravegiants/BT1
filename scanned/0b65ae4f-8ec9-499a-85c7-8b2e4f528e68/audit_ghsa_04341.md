# [C] YouTransfer has an issue in the sendmail transport integration that allows arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-68mc-h6h8-79wj
CVE: CVE-2026-50880
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-68mc-h6h8-79wj
Type: github-advisory

## Affected
- npm: `youtransfer` — affected >=0

## Details
An issue in the sendmail transport integration component of YouTransfer v1.0.6 allows attackers to execute arbitrary code via supplying a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50880
- https://gist.github.com/pyuysig/4013f4f10f74b3fded7ddf41b6d36ae5
- https://github.com/YouTransfer/YouTransfer
