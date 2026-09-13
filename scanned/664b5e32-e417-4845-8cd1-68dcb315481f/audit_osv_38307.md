# [C] CVE-2026-37751

## Summary
Severity: Critical
Advisory: CVE-2026-37751
Aliases: GHSA-mf7j-vfrr-jmfh
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-37751
Type: osv

## Details
An OS command injection vulnerability in the killSessionSync function (lib/agent-runtime.ts) of 23blocks-OS ai-maestro v0.24.17 allows attackers to execute arbitrary commands via a crafted input.

## References
- https://github.com/23blocks-OS/ai-maestro/security/advisories/GHSA-mf7j-vfrr-jmfh
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37751.json
- https://github.com/rajukani100/CVE-research/tree/main/ai-maestro-rce-advisory
- https://nvd.nist.gov/vuln/detail/CVE-2026-37751
- https://github.com/23blocks-OS/ai-maestro/commit/06d54f0687ad1fc5898a688a92f7e1f2df56c475
