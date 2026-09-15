# [C] Dokploy: Authenticated Remote Code Execution via Command Injection in /listen-deployment WebSocket Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-45629
Aliases: GHSA-r73h-qr3p-hf7f
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45629
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.28.8 and earlier, authenticated OS command injection in the /listen-deployment WebSocket endpoint allows any organization member to execute arbitrary system commands on remote servers managed by Dokploy, leading to full server compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45629.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-r73h-qr3p-hf7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45629
