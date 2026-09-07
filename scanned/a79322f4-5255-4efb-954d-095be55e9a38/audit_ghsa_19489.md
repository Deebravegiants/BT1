# [M] Moodle allows IDOR in RSS block, which allows access to additional RSS feeds

## Summary
Severity: Medium
Advisory: GHSA-chmf-m33p-ph8m
CVE: CVE-2025-3636
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-chmf-m33p-ph8m
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was found in Moodle. This vulnerability allows unauthorized users to access and view RSS feeds due to insufficient capability checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3636
- https://github.com/moodle/moodle/commit/0bd97209ac5e217dbec236c73e4f6fdcaee1c737
- https://access.redhat.com/security/cve/CVE-2025-3636
- https://bugzilla.redhat.com/show_bug.cgi?id=2359726
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467598
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-84499
