# [M] Moodle Vulnerable to Reflected Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-xhfx-rm8q-c3xv
CVE: CVE-2021-20183
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xhfx-rm8q-c3xv
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10 <4.0.0-beta

## Details
It was found in Moodle before version 4.0.0-beta that some search inputs were vulnerable to reflected Cross-site Scripting (XSS) due to insufficient escaping of search queries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20183
- https://github.com/moodle/moodle/commit/dc9de7b0d487b73c23c221dc0b8b6e01654921f3
- https://moodle.org/mod/forum/discuss.php?d=417166
