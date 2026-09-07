# [M] Moodle multiple cross-site scripting (XSS) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-grvw-qq2j-r898
CVE: CVE-2015-5336
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-grvw-qq2j-r898
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.7.11
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.9
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the survey module in Moodle through 2.6.11, 2.7.x before 2.7.11, 2.8.x before 2.8.9, and 2.9.x before 2.9.3 allow remote authenticated users to inject arbitrary web script or HTML by leveraging the student role and entering a crafted survey answer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5336
- https://github.com/moodle/moodle/commit/12c232df76885effa5ebac08e3094d6db5aa9223
- https://github.com/moodle/moodle/commit/31d0bf81af079bc285ea439ac5160f9e45697c88
- https://github.com/moodle/moodle/commit/48d8989f13a6320c54b05f7d3ea552356cf85ed6
- https://github.com/moodle/moodle/commit/86cec86942c1cfcb92b840afd18deed9b9a34951
- https://github.com/moodle/moodle/commit/b4f4232e1cf76334e4b8dda9cf68962b121e6bc0
- https://github.com/moodle/moodle/commit/f03ec4ce85b3d361429d9f66dbbb478a353640c9
- https://github.com/moodle/moodle/commit/fd14d2902fab15fa6affecc427bb11d3869d9afe
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=323231
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-49940
