# [H] Prototype Pollution in jquery-bbq

## Summary
Severity: High
Advisory: GHSA-7w8j-85wm-6xfq
CVE: CVE-2021-20086
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-7w8j-85wm-6xfq
Type: github-advisory

## Affected
- npm: `jquery-bbq` — affected >=0

## Details
Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution') in jquery-bbq 1.2.1 allows a malicious user to inject properties into Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20086
- https://github.com/BlackFan/client-side-prototype-pollution/blob/master/pp/jquery-bbq.md
- https://security.netapp.com/advisory/ntap-20241108-0002
