# [H] Moodle vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-273w-7fxj-pcp6
CVE: CVE-2021-36395
CWE: CWE-400, CWE-674
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-06
Source: https://github.com/advisories/GHSA-273w-7fxj-pcp6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0-beta <3.11.1
- Packagist: `moodle/moodle` — affected >=3.10.0-beta <3.10.5
- Packagist: `moodle/moodle` — affected >=0 <3.9.8

## Details
In Moodle, the file repository's URL parsing required additional recursion handling to mitigate the risk of recursion denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36395
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=424801
