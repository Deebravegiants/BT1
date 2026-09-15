# [C] Termix: OS Command Injection in Docker Container Management Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-42454
Aliases: GHSA-c2g2-hqgq-6w9v
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42454
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to version 2.1.0, all Docker container management endpoints in Termix interpolate the containerId URL path parameter and WebSocket message field directly into shell commands executed via ssh2.Client.exec() on remote managed servers without any sanitization or validation. An authenticated attacker can inject arbitrary OS commands by crafting a malicious container ID, achieving Remote Code Execution on any managed server. This issue has been patched in version 2.1.0.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.1.0-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42454.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-c2g2-hqgq-6w9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-42454
