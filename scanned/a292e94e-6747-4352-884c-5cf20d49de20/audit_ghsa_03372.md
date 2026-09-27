# [C] Prototype pollution in set-object-value

## Summary
Severity: Critical
Advisory: GHSA-4jj4-m52p-8rx3
CVE: CVE-2020-28281
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-4jj4-m52p-8rx3
Type: github-advisory

## Affected
- npm: `set-object-value` — affected >=0 <0.0.6

## Details
Prototype pollution vulnerability in 'set-object-value' versions 0.0.0 through 0.0.5 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28281
- https://github.com/react-atomic/react-atomic-organism/blob/e5645a2f9e632ffdebc83d720498831e09754c22/packages/lib/set-object-value/src/index.js#L16
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28281
