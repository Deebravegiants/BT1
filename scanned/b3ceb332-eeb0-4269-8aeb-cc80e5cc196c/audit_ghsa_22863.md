# [M] Moodle Open Redirect Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5xp2-rv4h-mm2q
CVE: CVE-2019-10133
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5xp2-rv4h-mm2q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.4
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.6
- Packagist: `moodle/moodle` — affected >=3.4.0 <3.4.9
- Packagist: `moodle/moodle` — affected >=0 <3.1.18

## Details
A flaw was found in Moodle before 3.7, 3.6.4, 3.5.6, 3.4.9 and 3.1.18. The form to upload cohorts contained a redirect field, which was not restricted to internal URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10133
- https://github.com/moodle/moodle/commit/5a89ac9640b3a695720845b6ddeff65e69a289fc
- https://github.com/moodle/moodle/commit/a6258d0934f707b1d033f50fb41ffbcf45bb2102
- https://github.com/moodle/moodle/commit/c509d108216524887c7ca08b1c451054d669ea75
- https://github.com/moodle/moodle/commit/cd6fb4322b6b1914c05f05033a71ed060f875fd4
- https://github.com/moodle/moodle/commit/d5067bffd230d733ad24f6aeaa56aaa17eca5bfb
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10133
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=386523
