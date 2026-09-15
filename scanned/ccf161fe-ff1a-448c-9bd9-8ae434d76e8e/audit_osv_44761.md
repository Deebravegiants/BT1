# [M] ntopng before 6.7.260717 Missing Authorization on the Notification Endpoint and Recipient Delete Handlers

## Summary
Severity: Medium
Advisory: CVE-2026-86090
Aliases: CVE-2026-86091, GHSA-m22w-f647-vx88
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-86090
Type: osv

## Details
ntopng before 6.7.260717 fails to perform authorization checks in the delete endpoints and recipients REST v2 handlers. Authenticated non-administrator users can issue POST requests to irreversibly delete all configured notification endpoints and recipients, silencing all alerts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86090.json
- https://github.com/ntop/ntopng/security/advisories/GHSA-m22w-f647-vx88
- https://nvd.nist.gov/vuln/detail/CVE-2026-86090
- https://www.vulncheck.com/advisories/ntopng-before-6.7.260717-missing-authorization-on-the-notification-endpoint-and-recipient-delete-handlers
- https://github.com/ntop/ntopng/commit/7d830f31af367745431c5d92e2e82fc432f6bdd8
- https://github.com/ntop/ntopng
- https://github.com/ntop/ntopng/blob/f41cc1beff90e40e12bbc2cc135bdbf649ec559f/scripts/lua/rest/v2/delete/endpoints.lua
- https://github.com/ntop/ntopng/blob/f41cc1beff90e40e12bbc2cc135bdbf649ec559f/scripts/lua/rest/v2/delete/recipients.lua
