# [M] Cross-site scripting in demos/demo.mysqli.php in getID3

## Summary
Severity: Medium
Advisory: GHSA-x2gw-85w6-fjjw
CVE: CVE-2021-40926
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-x2gw-85w6-fjjw
Type: github-advisory

## Affected
- Packagist: `james-heinrich/getid3` — affected >=1.0.0 <1.9.21

## Details
Cross-site scripting (XSS) vulnerability in demos/demo.mysqli.php in getID3 1.X and v2.0.0-beta allows remote attackers to inject arbitrary web script or HTML via the showtagfiles parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40926
- https://github.com/JamesHeinrich/getID3/issues/341
- https://github.com/JamesHeinrich/getID3/pull/342
- https://github.com/JamesHeinrich/getID3
- https://github.com/JamesHeinrich/getID3/releases/tag/v1.9.21
