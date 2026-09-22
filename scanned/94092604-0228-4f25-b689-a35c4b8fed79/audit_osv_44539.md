# [M] GROWI through 8.0.2 Missing Authorization on apiv3 Attachment Retrieval

## Summary
Severity: Medium
Advisory: CVE-2026-84204
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84204
Type: osv

## Details
GROWI contains an access control vulnerability in the GET /_api/v3/attachment/:id endpoint that fails to validate page access permissions. Authenticated attackers can retrieve attachment metadata from pages they cannot view by supplying known attachment identifiers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84204.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84204
- https://www.vulncheck.com/advisories/growi-through-8.0.2-missing-authorization-on-apiv3-attachment-retrieval
- https://github.com/growilabs/growi/commit/d298e0b1dbbf568c99db657fa0f7e90f72ddc59b
- https://github.com/growilabs/growi/pull/11810
- https://github.com/growilabs/growi
- https://github.com/growilabs/growi/blob/v8.0.2/apps/app/src/server/routes/apiv3/attachment.js
