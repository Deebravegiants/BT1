# [C] Termix Vulnerable to Remote Code Execution via SSH Tunnel Forward Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-45748
Aliases: GHSA-xmjh-8cc2-qm49
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45748
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. The `POST /ssh/tunnel/connect` endpoint in Termix prior to version 2.3.2 builds an SSH tunnel command by interpolating user-controlled host record fields (`endpointIP`, `endpointUsername`, `password`) directly into a shell command without escaping, allowing persistent OS command injection on the source SSH host. Version 2.3.2 patches the issue.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45748.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-xmjh-8cc2-qm49
- https://nvd.nist.gov/vuln/detail/CVE-2026-45748
