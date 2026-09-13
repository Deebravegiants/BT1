# [M] Open edX Platform: Account Activation Bypass via activation_key Exposure in REST API

## Summary
Severity: Medium
Advisory: CVE-2026-34736
Aliases: GHSA-m6rg-rp98-4crw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34736
Type: osv

## Details
Open edX Platform enables the authoring and delivery of online learning at any scale. From the maple release to before the ulmo release, an unauthenticated attacker can fully bypass the email verification process by combining two issues: the OAuth2 password grant issuing tokens to inactive users (documented behavior) and the activation_key being exposed in the REST API response at /api/user/v1/accounts/. This issue has been patched in the ulmo release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34736.json
- https://github.com/openedx/openedx-platform/security/advisories/GHSA-m6rg-rp98-4crw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34736
- https://github.com/openedx/openedx-platform/commit/ad342ae16e6af0b46460ca05f47697ac755feba8
