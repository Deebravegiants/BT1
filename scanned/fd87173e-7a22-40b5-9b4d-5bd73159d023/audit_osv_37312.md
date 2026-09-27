# [H] OneUptime: Path Traversal — Arbitrary File Read (No Auth)

## Summary
Severity: High
Advisory: CVE-2026-30958
Aliases: GHSA-p2wh-9pw8-hvff
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30958
Type: osv

## Details
OneUptime is a solution for monitoring and managing online services. Prior to 10.0.21, an unauthenticated path traversal in the /workflow/docs/:componentName endpoint allows reading arbitrary files from the server filesystem. The componentName route parameter is concatenated directly into a file path passed to res.sendFile() in orker/FeatureSet/Workflow/Index.ts with no sanitization or authentication middleware. This vulnerability is fixed in 10.0.21.

## References
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30958.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-p2wh-9pw8-hvff
- https://nvd.nist.gov/vuln/detail/CVE-2026-30958
