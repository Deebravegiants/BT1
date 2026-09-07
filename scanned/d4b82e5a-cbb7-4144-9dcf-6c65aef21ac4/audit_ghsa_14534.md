# [M] Moodle may allow students to bypass sequential navigation during a quiz attempt

## Summary
Severity: Medium
Advisory: GHSA-948f-j464-rfj2
CVE: CVE-2022-40208
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-948f-j464-rfj2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.0.0 <4.0.3
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.9
- Packagist: `moodle/moodle` — affected >=0 <3.9.16

## Details
In Moodle, insufficient limitations in some quiz web services made it possible for students to bypass sequential navigation during a quiz attempt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40208
- https://github.com/moodle/moodle/commit/025e0297b65e6a8bd61efad0fdf36168c613f918
- https://git.moodle.org/gw?p=moodle.git;a=commitdiff;h=025e0297b65e6a8bd61efad0fdf36168c613f918
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=438761
