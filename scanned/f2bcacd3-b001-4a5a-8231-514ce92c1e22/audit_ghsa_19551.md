# [M] Moodle has reflected Cross-site Scripting risk in policy tool

## Summary
Severity: Medium
Advisory: GHSA-hxgg-4qww-85ph
CVE: CVE-2025-3643
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-hxgg-4qww-85ph
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was found in Moodle. The return URL in the policy tool required additional sanitizing to prevent a reflected Cross-site scripting (XSS) risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3643
- https://github.com/moodle/moodle/commit/ff9bbd6d9e7d6267ce85e6c9afbeb19581f2a85f
- https://access.redhat.com/security/cve/CVE-2025-3643
- https://bugzilla.redhat.com/show_bug.cgi?id=2359742
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467604
