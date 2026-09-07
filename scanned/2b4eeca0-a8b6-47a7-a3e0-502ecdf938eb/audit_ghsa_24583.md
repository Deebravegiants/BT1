# [M] Moodle Persistent Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-q6vw-27c6-jv9c
CVE: CVE-2019-18210
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q6vw-27c6-jv9c
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7

## Details
Persistent XSS in `/course/modedit.php` of Moodle through 3.7.2 allows authenticated users (Teacher and above) to inject JavaScript into the session of another user (e.g., enrolled student or site administrator) via the introeditor[text] parameter. NOTE: the discoverer and vendor disagree on whether Moodle customers have a reasonable expectation that anyone authenticated as a Teacher can be trusted with the ability to add arbitrary JavaScript (this ability is not documented on Moodle's Teacher_role page). Because the vendor has this expectation, they have stated "this report has been closed as a false positive, and not a bug."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18210
- https://docs.moodle.org/38/en/Teacher_role
- https://gist.github.com/Danbardo/4a6b0fe8cb21ec6d7c54e6ac951bdb0a
- https://github.com/moodle/moodle
