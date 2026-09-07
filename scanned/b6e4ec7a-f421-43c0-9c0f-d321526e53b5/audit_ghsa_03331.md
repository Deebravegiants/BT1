# [C] Prototype Pollution in set-or-get

## Summary
Severity: Critical
Advisory: GHSA-6rv4-4qv6-88g2
CVE: CVE-2021-25913
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-12
Source: https://github.com/advisories/GHSA-6rv4-4qv6-88g2
Type: github-advisory

## Affected
- npm: `set-or-get` — affected >=1.0.0 <1.2.11

## Details
Prototype pollution vulnerability in ‘set-or-get’ version 1.0.0 through 1.2.10 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25913
- https://github.com/IonicaBizau/set-or-get.js/commit/82ede5cccb2e8d13e4f62599203a4389f6d8e936
- https://www.npmjs.com/package/set-or-get
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25913
