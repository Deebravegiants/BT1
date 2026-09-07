# [M] Bolt Cross-site Scripting (XSS) via text input click preview button

## Summary
Severity: Medium
Advisory: GHSA-gjx6-58xh-p7pw
CVE: CVE-2018-19933
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gjx6-58xh-p7pw
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0 <3.6.2

## Details
Bolt CMS <3.6.2 allows XSS via text input click preview button as demonstrated by the Title field of a Configured and New Entry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19933
- https://github.com/bolt/bolt
- https://github.com/rdincel1/Bolt-CMS-3.6.2---Cross-Site-Scripting
- https://www.exploit-db.com/exploits/46014
- https://www.raifberkaydincel.com/bolt-cms-xss-vulnerability.html
