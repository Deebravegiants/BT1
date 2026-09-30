# [M] GROWI through 8.0.2 Authorization Bypass Through User-Controlled Key on apiv3 Revision Retrieval

## Summary
Severity: Medium
Advisory: CVE-2026-84205
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84205
Type: osv

## Details
GROWI contains an access control vulnerability in the GET /_api/v3/revisions/:id endpoint that validates access against a query parameter but returns the revision identified by the path parameter without confirming they reference the same page. Authenticated attackers can pair a page identifier they can access with an arbitrary revision identifier to read revision content from pages they lack permission to view.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84205.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84205
- https://www.vulncheck.com/advisories/growi-through-8.0.2-authorization-bypass-through-user-controlled-key-on-apiv3-revision-retrieval
- https://github.com/growilabs/growi/commit/d298e0b1dbbf568c99db657fa0f7e90f72ddc59b
- https://github.com/growilabs/growi/pull/11810
- https://github.com/growilabs/growi
- https://github.com/growilabs/growi/blob/v8.0.2/apps/app/src/server/routes/apiv3/revisions.js
