# [M] Moodle's IDOR in Feedback non-respondents report allows messaging arbitrary site users

## Summary
Severity: Medium
Advisory: GHSA-p9cx-f595-h79h
CVE: CVE-2024-43438
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-p9cx-f595-h79h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.12
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.9
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.6
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.2

## Details
A flaw was found in Feedback. Bulk messaging in the activity's non-respondents report did not verify message recipients belonging to the set of users returned by the report.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43438
- https://bugzilla.redhat.com/show_bug.cgi?id=2304267
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461208
