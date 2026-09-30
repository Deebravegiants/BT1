# [H] Unauthenticated Remote Code Execution via P2P Sharing in ZAI-Shell

## Summary
Severity: High
Advisory: CVE-2026-25807
Aliases: GHSA-6pjj-r955-34rr
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25807
Type: osv

## Details
ZAI Shell is an autonomous SysOps agent designed to navigate, repair, and secure complex environments. Prior to 9.0.3, the P2P terminal sharing feature (share start) opens a TCP socket on port 5757 without any authentication mechanism. Any remote attacker can connect to this port using a simple socket script. An attacker who connects to a ZAI-Shell P2P session running in --no-ai mode can send arbitrary system commands. If the host user approves the command without reviewing its contents, the command executes directly with the user's privileges, bypassing all Sentinel safety checks. This vulnerability is fixed in 9.0.3.

## References
- https://github.com/TaklaXBR/zai-shell/releases/tag/v9.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25807.json
- https://github.com/TaklaXBR/zai-shell/security/advisories/GHSA-6pjj-r955-34rr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25807
- https://github.com/TaklaXBR/zai-shell/commit/a4ea8525d912f55d6e2f09b2869966c52d189a4a
