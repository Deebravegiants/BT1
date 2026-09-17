# [M] Wekan Exposes All Global Webhook Integrations through globalwebhooks Publication

## Summary
Severity: Medium
Advisory: CVE-2026-30846
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:L/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-30846
Type: osv

## Details
Wekan is an open source kanban tool built with Meteor. In versions 8.31.0 through 8.33, the globalwebhooks publication exposes all global webhook integrations—including sensitive url and token fields—without performing any authentication check on the server side. Although the subscription is normally invoked from the admin settings page, the server-side publication has no access control, meaning any DDP client, including unauthenticated ones, can subscribe and receive the data. This allows an unauthenticated attacker to retrieve global webhook URLs and authentication tokens, potentially enabling unauthorized use of those webhooks and access to connected external services. This issue has been fixed in version 8.34.

## References
- https://github.com/wekan/wekan/releases/tag/v8.34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30846.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30846
- https://securitylab.github.com/advisories/GHSL-2026-037_Wekan/
- https://github.com/wekan/wekan/commit/1ee9b2e917104f54c035f6426169a28fedecbdb6
