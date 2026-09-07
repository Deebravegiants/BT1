# [M] Moodle Insecure direct object reference (IDOR) in a calendar web service

## Summary
Severity: Medium
Advisory: GHSA-g39c-mccf-rxjv
CVE: CVE-2021-43560
CWE: CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g39c-mccf-rxjv
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.11
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.8
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.4

## Details
A flaw was found in Moodle in versions 3.11 to 3.11.3, 3.10 to 3.10.7, 3.9 to 3.9.10 and earlier unsupported versions. Insufficient capability checks made it possible to fetch other users' calendar action events.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43560
- https://bugzilla.redhat.com/show_bug.cgi?id=2021519
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=429100
