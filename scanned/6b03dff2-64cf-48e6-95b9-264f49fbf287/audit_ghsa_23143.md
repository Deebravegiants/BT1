# [M] Moodle Cross-site Scripting in the Course summary filter of the Add a new course

## Summary
Severity: Medium
Advisory: GHSA-4m6v-x9fj-847j
CVE: CVE-2017-7298
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4m6v-x9fj-847j
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.2

## Details
In Moodle 3.2.2+, there is XSS in the Course summary filter of the "Add a new course" page, as demonstrated by a crafted attribute of an SVG element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7298
- https://github.com/moodle/moodle
- http://www.daimacn.com/index.php/post/12.html
- http://www.daimacn.com/post/12.html
- http://www.securityfocus.com/bid/97182
