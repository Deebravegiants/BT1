# [H] Moodle has an authenticated remote code execution risk in the Moodle LMS EQUELLA repository

## Summary
Severity: High
Advisory: GHSA-m367-445c-2xqr
CVE: CVE-2025-3642
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-m367-445c-2xqr
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was found in Moodle. A remote code execution risk was identified in the Moodle LMS EQUELLA repository. By default, this was only available to teachers and managers on sites with the EQUELLA repository enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3642
- https://github.com/moodle/moodle/commit/630fbf6230ee18d63ce69bea34173fb151b599da
- https://access.redhat.com/security/cve/CVE-2025-3642
- https://bugzilla.redhat.com/show_bug.cgi?id=2359738
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467603
