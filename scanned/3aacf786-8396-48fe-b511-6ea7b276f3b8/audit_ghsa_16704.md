# [M] verbb/formie Server-Side Template Injection for variable-enabled settings

## Summary
Severity: Medium
Advisory: GHSA-v45m-hxqp-fwf5
CVE: CVE-2024-35191
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-v45m-hxqp-fwf5
Type: github-advisory

## Affected
- Packagist: `verbb/formie` — affected >=0 <2.1.6

## Details
### Impact
Users with access to a form's settings can include malicious Twig code into fields that support Twig. These might be the Submission Title or the Success Message. This code will then be executed upon creating a submission, or rendering the text.

This is listed as low-medium severity due to requiring control panel access to edit a form's settings.

### Patches
This has been fixed in Formie 2.1.6. Users should ensure they are running at least this version.

## References
- https://github.com/verbb/formie/security/advisories/GHSA-v45m-hxqp-fwf5
- https://nvd.nist.gov/vuln/detail/CVE-2024-35191
- https://github.com/verbb/formie/commit/90296edf7e707f117e760aa57e70dbd43a854420
- https://github.com/verbb/formie
