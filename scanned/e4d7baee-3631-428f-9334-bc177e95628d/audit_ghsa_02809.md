# [C] Prototype pollution in getobject

## Summary
Severity: Critical
Advisory: GHSA-957j-59c2-j692
CVE: CVE-2020-28282
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-957j-59c2-j692
Type: github-advisory

## Affected
- npm: `getobject` — affected >=0 <1.0.0

## Details
Prototype pollution vulnerability in 'getobject' version 0.1.0 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28282
- https://github.com/cowboy/node-getobject
- https://github.com/cowboy/node-getobject/blob/aba04a8e1d6180eb39eff09990c3a43886ba8937/lib/getobject.js#L48
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28282
