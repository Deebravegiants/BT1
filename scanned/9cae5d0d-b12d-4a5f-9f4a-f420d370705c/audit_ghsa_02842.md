# [M] Exposure of Sensitive Information to an Unauthorized Actor in Moodle

## Summary
Severity: Medium
Advisory: GHSA-c7v4-m269-4995
CVE: CVE-2020-25703
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-10-21
Source: https://github.com/advisories/GHSA-c7v4-m269-4995
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.3
- Packagist: `moodle/moodle` — affected >=3.8.0 <3.8.6
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.9
- Packagist: `moodle/moodle` — affected >=3.10.0-beta <3.10.0

## Details
The participants table download in Moodle always included user emails, but should have only done so when users' emails are not hidden. Versions affected: 3.9 to 3.9.2, 3.8 to 3.8.5 and 3.7 to 3.7.8. This is fixed in moodle 3.9.3, 3.8.6, 3.7.9, and 3.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25703
- https://bugzilla.redhat.com/show_bug.cgi?id=1895439
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4NNFCHPPHRJNJROIX6SYMHOC6HMKP3GU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B55KXBVAT45MDASJ3EK6VIGQOYGJ4NH6
- https://moodle.org/mod/forum/discuss.php?d=413941
