# [C] Moodle Oauth 2 Insufficiently Protects Against Compromise

## Summary
Severity: Critical
Advisory: GHSA-rv62-6f56-j83w
CVE: CVE-2019-14880
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rv62-6f56-j83w
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.3
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.7
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.9

## Details
A vulnerability was found in Moodle versions 3.7 before 3.7.3, 3.6 before 3.6.7, 3.5 before 3.5.9 and earlier. OAuth 2 providers who do not verify users' email address changes require additional verification during sign-up to reduce the risk of account compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14880
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14880
- https://github.com/moodle/moodle
