# [H] Bludit's persistent authentication tokens not revoked upon account disablement

## Summary
Severity: High
Advisory: CVE-2026-46657
Aliases: GHSA-ggqg-xvx6-hgwh
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46657
Type: osv

## Details
Bludit is a content management system. Versions prior to 3.22.0 have a vulnerability in the user management logic that allows deactivated accounts to maintain access via persistent authentication tokens. When an administrator disables a user account, the application fails to invalidate or clear the associated tokenAuth and tokenRemember fields in the JSON database. Consequently, any user with a pre-existing "Remember Me" cookie can bypass the account disablement and maintain a valid authenticated state. Version 3.22.0 patches the issue.

## References
- https://github.com/bludit/bludit/releases/tag/3.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46657.json
- https://github.com/bludit/bludit/security/advisories/GHSA-ggqg-xvx6-hgwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46657
