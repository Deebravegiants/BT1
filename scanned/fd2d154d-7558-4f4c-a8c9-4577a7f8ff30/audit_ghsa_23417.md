# [M] Moodle Logged in users could view all calendar events

## Summary
Severity: Medium
Advisory: GHSA-45rw-4r25-jvg7
CVE: CVE-2019-3848
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-45rw-4r25-jvg7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.8
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.5
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.3

## Details
A vulnerability was found in moodle before versions 3.6.3, 3.5.5 and 3.4.8. Permissions were not correctly checked before loading event information into the calendar's edit event modal popup, so logged in non-guest users could view unauthorised calendar events. (Note: It was read-only access, users could not edit the events.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3848
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3848
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=384011#p1547743
