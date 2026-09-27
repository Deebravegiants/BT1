# [H] CVE-2025-65781

## Summary
Severity: High
Advisory: CVE-2025-65781
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-65781
Type: osv

## Details
An issue was discovered in Wekan The Open Source kanban board system up to version 18.15, fixed in 18.16. Attachment upload API treats the Authorization bearer value as a userId and enters a non-terminating body-handling branch for any non-empty bearer token, enabling trivial application-layer DoS and latent identity-spoofing.

## References
- https://github.com/wekan/wekan/blob/main/CHANGELOG.md#v816-2025-11-02-wekan--release
- https://wekan.fi/hall-of-fame/spacebleed/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65781.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65781
- https://github.com/wekan/wekan/commit/ccd90343394f433b287733ad0a33c08e0a71f53c
- https://github.com/wekan/wekan
