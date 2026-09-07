# [M] MCP NMAP Server has an Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xc68-rrqc-qgq3
CVE: CVE-2026-3484
CWE: CWE-74, CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-xc68-rrqc-qgq3
Type: github-advisory

## Affected
- npm: `mcp-nmap-server` — affected >=0

## Details
A vulnerability was detected in PhialsBasement nmap-mcp-server up to bee6d23547d57ae02460022f7c78ac0893092e38. Affected by this issue is the function child_process.exec of the file src/index.ts of the component Nmap CLI Command Handler. The manipulation results in command injection. The attack may be performed from remote. This product utilizes a rolling release system for continuous delivery, and as such, version information for affected or updated releases is not disclosed. The patch is identified as 30a6b9e1c7fa6146f51e28d6ab83a2568d9a3488. It is best practice to apply a patch to resolve this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3484
- https://github.com/PhialsBasement/nmap-mcp-server/issues/7
- https://github.com/PhialsBasement/nmap-mcp-server/issues/7#issuecomment-3814382570
- https://github.com/PhialsBasement/nmap-mcp-server/commit/30a6b9e1c7fa6146f51e28d6ab83a2568d9a3488
- https://github.com/PhialsBasement/nmap-mcp-server
- https://vuldb.com/?ctiid.348559
- https://vuldb.com/?id.348559
- https://vuldb.com/?submit.763773
- https://vuldb.com/?submit.763777
