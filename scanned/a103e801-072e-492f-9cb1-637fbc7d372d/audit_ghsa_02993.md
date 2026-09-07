# [C] Moodle vulnerable to RCE via unsafe deserialization

## Summary
Severity: Critical
Advisory: GHSA-8jhp-2gcr-qw96
CVE: CVE-2021-3943
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-8jhp-2gcr-qw96
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.4
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.8
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.11

## Details
A flaw was found in Moodle in versions 3.11 to 3.11.3, 3.10 to 3.10.7, 3.9 to 3.9.10 and earlier unsupported versions. A remote code execution risk when restoring backup files was identified.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3943
- https://github.com/moodle/moodle/commit/58e8ad852f9e75c8158e5bee02c273383f7d9865
- https://bugzilla.redhat.com/show_bug.cgi?id=2021963
- https://moodle.org/mod/forum/discuss.php?d=429095
