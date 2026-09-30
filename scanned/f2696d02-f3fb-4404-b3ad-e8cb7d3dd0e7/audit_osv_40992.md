# [M] ZITADEL: Auto-linking by email: IdP-side email verification is not checked

## Summary
Severity: Medium
Advisory: CVE-2026-56666
Aliases: GHSA-992q-9gwp-7r79
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56666
Type: osv

## Details
ZITADEL is an open source identity management platform. Prior to 4.15.3, ZITADEL's external identity provider handler checks that the local user's email is verified but does not verify that the external IdP confirmed ownership of the same email before auto-linking by email, allowing a permissive provider account with a victim email address to be linked to the victim's local account. This issue is fixed in version 4.15.3.

## References
- https://github.com/zitadel/zitadel/releases/tag/v4.15.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56666.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-992q-9gwp-7r79
- https://nvd.nist.gov/vuln/detail/CVE-2026-56666
- https://github.com/zitadel/zitadel/commit/c97012f0c5dc2fe960ae6e940cbea23229f0557f
