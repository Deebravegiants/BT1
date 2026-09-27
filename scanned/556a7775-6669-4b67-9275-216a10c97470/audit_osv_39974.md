# [H] TypeBot has Arbitrary S3 Object Write in deprecated public upload endpoint via attacker-controlled filePath

## Summary
Severity: High
Advisory: CVE-2026-48763
Aliases: GHSA-m7f5-3wcm-x2c4
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48763
Type: osv

## Details
TypeBot is a chatbot builder tool. Versions prior to 3.17.0 expose a deprecated public upload endpoint at `GET /api/v1/typebots/{typebotId}/blocks/{blockId}/storage/upload-url` that accepts an attacker-controlled `filePath` and returns a presigned S3 `PUT` URL for that exact key. Because the endpoint only checks that the referenced typebot is public and that the referenced block is a file input block, an unauthenticated attacker who knows a valid public `typebotId` and `blockId` can request presigned upload URLs for arbitrary objects in the shared bucket, including `private/...` and other tenants' `public/...` paths. Version 3.17.0 fixes this issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48763.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-m7f5-3wcm-x2c4
- https://nvd.nist.gov/vuln/detail/CVE-2026-48763
- https://github.com/baptisteArno/typebot.io/commit/7ae4c007d0987d2ca907b47e1b7418db62b8a157
- https://github.com/baptisteArno/typebot.io/pull/2459
