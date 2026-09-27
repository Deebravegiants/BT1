# [M] Logto Server-Side Request Forgery via webhook test endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-82262
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82262
Type: osv

## Details
Logto through 1.42.0 contains a server-side request forgery vulnerability in the POST /api/hooks/:id/test endpoint that accepts arbitrary URLs without host validation. Tenant administrators with Management API tokens can make the server issue HTTP POST requests to internal URLs and retrieve response bodies from services on the private network.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82262
- https://www.vulncheck.com/advisories/logto-server-side-request-forgery-via-webhook-test-endpoint
- https://github.com/logto-io/logto/issues/9465
- https://github.com/logto-io/logto/commit/16f4b2e732d5114ac98646c9370ec6ab61d6ed26
- https://github.com/logto-io/logto
- https://github.com/logto-io/logto/blob/v1.42.0/packages/core/src/libraries/hook/utils.ts
