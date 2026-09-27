# [H] link-preview-js DNS Rebinding SSRF Bypass / Incomplete Fix for CVE-2026-43897

## Summary
Severity: High
Advisory: CVE-2026-61704
Aliases: GHSA-cpjf-6666-r8fx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-61704
Type: osv

## Details
Link Preview JS extracts web links information. Prior to 4.0.4, the resolveDNSHost mitigation in index.ts validates one resolved IP address but fetches the original hostname, allowing an attacker-controlled DNS server to return a public address during validation and a loopback or internal address during the final connection. This DNS rebinding condition bypasses the SSRF protection and can cause the server-side preview fetch to reach internal HTTP resources. Redirect handling is affected by the same validation-to-fetch mismatch. This issue is fixed in version 4.0.4.

## References
- https://github.com/OP-Engineering/link-preview-js/releases/tag/4.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61704.json
- https://github.com/OP-Engineering/link-preview-js/security/advisories/GHSA-cpjf-6666-r8fx
- https://nvd.nist.gov/vuln/detail/CVE-2026-61704
- https://github.com/OP-Engineering/link-preview-js/commit/6ee25043dd60b097eb70b4ce049aac94b28239e3
- https://github.com/OP-Engineering/link-preview-js/commit/f3a3dd84adbb9d32d06a933f44ff3eaa837f9a12
- https://github.com/OP-Engineering/link-preview-js/pull/181
