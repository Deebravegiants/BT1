# [C] Prototype pollution in set-in

## Summary
Severity: Critical
Advisory: GHSA-qr4p-c9wr-phr6
CVE: CVE-2020-28273
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-qr4p-c9wr-phr6
Type: github-advisory

## Affected
- npm: `set-in` — affected >=0 <2.0.1

## Details
Prototype pollution vulnerability in 'set-in' versions 1.0.0 through 2.0.0 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28273
- https://github.com/ahdinosaur/set-in/commit/e431effa00195a6f06b111e09733cd1445a91a88
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28273
