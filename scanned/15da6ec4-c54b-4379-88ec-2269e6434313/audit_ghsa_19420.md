# [M] Moodle makes some user data available before completing second factor with MFA enabled

## Summary
Severity: Medium
Advisory: GHSA-x45j-jq9q-gf3q
CVE: CVE-2025-3627
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-x45j-jq9q-gf3q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A security vulnerability was discovered in Moodle that allows some users to access sensitive information about other students before they finish verifying their identities using two-factor authentication (2FA).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3627
- https://access.redhat.com/security/cve/CVE-2025-3627
- https://bugzilla.redhat.com/show_bug.cgi?id=2359692
- https://github.com/moodle/moodle
- https://github.com/search?q=repo%3Amoodle%2Fmoodle+MDL-84351&type=commits
- https://moodle.org/mod/forum/discuss.php?d=467594
