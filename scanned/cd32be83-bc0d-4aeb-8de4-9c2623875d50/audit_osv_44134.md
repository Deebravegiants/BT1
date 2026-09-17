# [M] GROWI before 8.0.2 Missing Authorization on Attachment Retrieval for Unauthenticated Requests

## Summary
Severity: Medium
Advisory: CVE-2026-80191
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80191
Type: osv

## Details
GROWI applies its page-viewer permission check to attachment requests only when the request carries an authenticated user. retrieveAttachmentFromIdParam in apps/app/src/server/routes/attachment/get.ts guards the check with a condition requiring the user to be non-null, so a request that carries no session skips the check entirely and the handler returns the file. The routes reached this way, /attachment/:id and /download/:id, take the attachment identifier from the path, so an unauthenticated caller who has an attachment identifier receives the file regardless of whether the page owning it is private and regardless of whether that caller would be permitted to view the page. Identifiers can be retained by a user whose access was later removed, or recovered from anywhere the identifier was previously exposed. Version 8.0.2 runs the check for authenticated and unauthenticated requests alike, skipping it only where a valid share link has already bound the requested file to that link's page.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80191.json
- https://github.com/growilabs/growi/releases/tag/v8.0.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-80191
- https://www.vulncheck.com/advisories/growi-before-8.0.2-missing-authorization-on-attachment-retrieval-for-unauthenticated-requests
- https://github.com/growilabs/growi/pull/11756
- https://github.com/growilabs/growi
- https://github.com/growilabs/growi/blob/v8.0.1/apps/app/src/server/routes/attachment/get.ts
