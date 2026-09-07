# [M] Insufficient user authorization in Moodle

## Summary
Severity: Medium
Advisory: GHSA-93pj-4p65-qmr9
CVE: CVE-2022-0334
CWE: CWE-668, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-93pj-4p65-qmr9
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.5
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.8
- Packagist: `moodle/moodle` — affected >=0 <3.9.11

## Details
A flaw was found in Moodle in versions 3.11 to 3.11.4, 3.10 to 3.10.8, 3.9 to 3.9.11 and earlier unsupported versions. Insufficient capability checks could lead to users accessing their grade report for courses where they did not have the required gradereport/user:view capability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0334
- https://github.com/moodle/moodle/commit/1964d68f8500ea3c7b776fa8a2af6266ed109f84
- https://github.com/moodle/moodle/commit/6d18f136ae88ec97e351a723df570816a959ec68
- https://bugzilla.redhat.com/show_bug.cgi?id=2043664
- https://moodle.org/mod/forum/discuss.php?d=431102
