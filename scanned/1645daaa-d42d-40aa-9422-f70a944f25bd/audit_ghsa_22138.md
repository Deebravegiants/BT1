# [M] Bolt Cross-site Scripting via the slug, teaser or title parameters

## Summary
Severity: Medium
Advisory: GHSA-2g23-qmmp-fvmr
CVE: CVE-2019-9553
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2g23-qmmp-fvmr
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected 3.6.4

## Details
Bolt 3.6.4 has XSS via the slug, teaser, or title parameter to `editcontent/pages`, a related issue to CVE-2017-11128 and CVE-2018-19933.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9553
- https://github.com/bolt/bolt
- https://packetstormsecurity.com/files/151943/Bold-CMS-3.6.4-Cross-Site-Scripting.html
- https://www.exploit-db.com/exploits/46495
