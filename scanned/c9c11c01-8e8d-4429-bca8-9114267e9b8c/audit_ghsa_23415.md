# [H] Zenario CMS vulnerable to CSRF 

## Summary
Severity: High
Advisory: GHSA-22cq-xxr9-jrrv
CVE: CVE-2018-18420
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-22cq-xxr9-jrrv
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0

## Details
Cross-Site Request Forgery (CSRF) vulnerability was discovered in the 8.3 version of Zenario Content Management System via the `admin/organizer.ajax.php?path=zenario__content%2Fpanels%2Fcontent` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18420
- http://packetstormsecurity.com/files/149851/Zenar-Content-Management-System-8.3-Cross-Site-Request-Forgery.html
