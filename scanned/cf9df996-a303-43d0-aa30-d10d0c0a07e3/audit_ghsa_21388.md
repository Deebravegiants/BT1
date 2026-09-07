# [H] Moodle Stored Cross-site Scripting and page denial of service

## Summary
Severity: High
Advisory: GHSA-jqgr-gh62-jf53
CVE: CVE-2022-40313
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-jqgr-gh62-jf53
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.17
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.10
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.4

## Details
Recursive rendering of Mustache template helpers containing user input could, in some cases, result in an Cross-site Scripting risk or a page failing to load.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40313
- https://bugzilla.redhat.com/show_bug.cgi?id=2128146
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=438392
