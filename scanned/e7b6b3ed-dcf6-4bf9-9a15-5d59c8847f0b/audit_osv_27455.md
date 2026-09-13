# [C] Remote code execution on ReconServer due to improper input sanitization on the prips command

## Summary
Severity: Critical
Advisory: CVE-2024-21663
Aliases: GHSA-fjcj-g7x8-4rp7
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2024-21663
Type: osv

## Details
Discord-Recon is a Discord bot created to automate bug bounty recon, automated scans and information gathering via a discord server. Discord-Recon is vulnerable to remote code execution. An attacker is able to execute shell commands in the server without having an admin role. This vulnerability has been fixed in version 0.0.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21663.json
- https://github.com/DEMON1A/Discord-Recon/security/advisories/GHSA-fjcj-g7x8-4rp7
- https://nvd.nist.gov/vuln/detail/CVE-2024-21663
- https://github.com/DEMON1A/Discord-Recon/issues/23
- https://github.com/DEMON1A/Discord-Recon/commit/f9cb0f67177f5e2f1022295ca8e641e47837ec7a
