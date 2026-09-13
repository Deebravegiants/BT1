# [H] LibreChat has SSRF protection bypass via IPv4-mapped IPv6 normalization in isPrivateIP

## Summary
Severity: High
Advisory: CVE-2026-31943
Aliases: GHSA-w5r7-4f94-vp4c
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-31943
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Prior to version 0.8.3, `isPrivateIP()` in `packages/api/src/auth/domain.ts` fails to detect IPv4-mapped IPv6 addresses in their hex-normalized form, allowing any authenticated user to bypass SSRF protection and make the server issue HTTP requests to internal network resources — including cloud metadata services (e.g., AWS `169.254.169.254`), loopback, and RFC1918 ranges. Version 0.8.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31943.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-w5r7-4f94-vp4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-31943
