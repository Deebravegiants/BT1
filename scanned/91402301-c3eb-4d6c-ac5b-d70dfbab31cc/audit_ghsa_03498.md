# [M] Privilage Escalation in moodle

## Summary
Severity: Medium
Advisory: GHSA-c9hq-g4q8-w893
CVE: CVE-2020-25701
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-c9hq-g4q8-w893
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.3
- Packagist: `moodle/moodle` — affected >=3.8.0 <3.8.6
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.9
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.15

## Details
If the upload course tool in Moodle was used to delete an enrollment method which did not exist or was not already enabled, the tool would erroneously enable that enrollment method. This could lead to unintended users gaining access to the course. Versions affected: 3.9 to 3.9.2, 3.8 to 3.8.5, 3.7 to 3.7.8, 3.5 to 3.5.14 and earlier unsupported versions. This is fixed in moodle 3.9.3, 3.8.6, 3.7.9, 3.5.15, and 3.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25701
- https://github.com/moodle/moodle/commit/b8e1eec4c77c858de87fedf4e405e929539ea0c5
- https://bugzilla.redhat.com/show_bug.cgi?id=1895432
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4NNFCHPPHRJNJROIX6SYMHOC6HMKP3GU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B55KXBVAT45MDASJ3EK6VIGQOYGJ4NH6
- https://moodle.org/mod/forum/discuss.php?d=413939
