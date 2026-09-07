# [M] Moodle Client side denial of service via personal message

## Summary
Severity: Medium
Advisory: GHSA-c3j6-33r4-89q3
CVE: CVE-2021-20185
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c3j6-33r4-89q3
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.16
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.7
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.4
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.1

## Details
It was found in Moodle before version 3.10.1, 3.9.4, 3.8.7 and 3.5.16 that messaging did not impose a character limit when sending messages, which could result in client-side (browser) denial of service for users receiving very large messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20185
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=417168
