# [M] LibreChat Affected by Arbitrary File Write via `execute_code` Artifact Filename Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-34371
Aliases: GHSA-qrm5-r67f-6692
CVSS: 6.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-34371
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Prior to 0.8.4, LibreChat trusts the name field returned by the execute_code sandbox when persisting code-generated artifacts. On deployments using the default local file strategy, a malicious artifact filename containing traversal sequences (for example, ../../../../../app/client/dist/poc.txt) is concatenated into the server-side destination path and written with fs.writeFileSync() without sanitization. This gives any user who can trigger execute_code an arbitrary file write primitive as the LibreChat server user. This vulnerability is fixed in 0.8.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34371.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-qrm5-r67f-6692
- https://nvd.nist.gov/vuln/detail/CVE-2026-34371
