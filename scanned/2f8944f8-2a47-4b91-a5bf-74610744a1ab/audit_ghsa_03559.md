# [M] SQL Injection in moodle

## Summary
Severity: Medium
Advisory: GHSA-7h8v-2v8x-h264
CVE: CVE-2020-25700
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-7h8v-2v8x-h264
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.3
- Packagist: `moodle/moodle` — affected >=3.8.0 <3.8.6
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.9
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.15

## Details
In moodle, some database module web services allowed students to add entries within groups they did not belong to. Versions affected: 3.9 to 3.9.2, 3.8 to 3.8.5, 3.7 to 3.7.8, 3.5 to 3.5.14 and earlier unsupported versions. This is fixed in moodle 3.8.6, 3.7.9, 3.5.15, and 3.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25700
- https://github.com/moodle/moodle/commit/8169aeff59d8ed910ca3545413561005282bbd32
- https://bugzilla.redhat.com/show_bug.cgi?id=1895427
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4NNFCHPPHRJNJROIX6SYMHOC6HMKP3GU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B55KXBVAT45MDASJ3EK6VIGQOYGJ4NH6
- https://moodle.org/mod/forum/discuss.php?d=413938
