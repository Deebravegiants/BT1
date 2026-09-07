# [C] Prototype pollution in 101

## Summary
Severity: Critical
Advisory: GHSA-cwcx-rxgc-cmw3
CVE: CVE-2021-25943
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-cwcx-rxgc-cmw3
Type: github-advisory

## Affected
- npm: `101` — affected >=1.0.0

## Details
Prototype pollution vulnerability in '101' versions 1.0.0 through 1.6.3 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25943
- https://github.com/tjmehta/101
- https://github.com/tjmehta/101/blob/d87f63ce2a4cbdc476e8287abd78327c3144d646/set.js#L52
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25943
