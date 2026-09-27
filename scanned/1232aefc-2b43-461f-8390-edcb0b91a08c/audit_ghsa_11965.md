# [H] Craft CMS vulnerable to behavior injection RCE ElementIndexesController and FieldsController

## Summary
Severity: High
Advisory: GHSA-4484-8v2f-5748
CVE: CVE-2026-32264
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-4484-8v2f-5748
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.5
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.11

## Details
The fix for https://github.com/advisories/GHSA-7jx7-3846-m7w7 (commit https://github.com/craftcms/cms/commit/395c64f0b80b507be1c862a2ec942eaacb353748) only patched `src/services/Fields.php`, but the same vulnerable pattern exists in `ElementIndexesController` and `FieldsController`.

You need Craft control panel administrator permissions, and allowAdminChanges must be enabled for this to work.

An attacker can use the same gadget chain from the original advisory to achieve RCE.

Users should update to Craft 4.17.5 and 5.9.11 to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-4484-8v2f-5748
- https://github.com/craftcms/cms/security/advisories/GHSA-7jx7-3846-m7w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32264
- https://github.com/craftcms/cms/commit/78d181e12e0b15e1300f54ec85f19859d3300f70
- https://github.com/craftcms/cms/commit/dfec46362fcb40b330ce8a4d8136446e65085620
- https://github.com/craftcms/cms
