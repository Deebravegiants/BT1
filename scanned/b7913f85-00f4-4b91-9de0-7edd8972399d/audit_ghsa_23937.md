# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7ghm-fp7p-qvjq
CVE: CVE-2016-9188
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7ghm-fp7p-qvjq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.1

## Details
Cross-site scripting (XSS) vulnerabilities in Moodle CMS on or before 3.1.2 allow remote attackers to inject arbitrary web script or HTML via the s_additionalhtmlhead, s_additionalhtmltopofbody, and s_additionalhtmlfooter parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9188
- https://packetstormsecurity.com/files/139466/Moodle-CMS-3.1.2-Cross-Site-Scripting-File-Upload.html
- https://web.archive.org/web/20210123190812/http://www.securityfocus.com/bid/94189
