# [M] LibreChat: Image Upload Route Bypasses Agent Permission Check — Incomplete Fix for File Upload Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-54027
Aliases: GHSA-c55r-p24w-hcj5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54027
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, the POST /api/files/images endpoint allows any authenticated user to upload files into any agent's tool_resources (e.g., context, execute_code) without verifying ownership or EDIT permission on the target agent. A permission check was added to the POST /api/files route in a previous patch, but the image upload route was never updated with the same check. An attacker can simply use the image endpoint instead of the file endpoint to bypass the authorization entirely. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54027.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-c55r-p24w-hcj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54027
