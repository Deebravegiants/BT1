# [C] Network-AI SandboxPolicy before 5.15.1 Blocklist Bypass via Quote Mismatch

## Summary
Severity: Critical
Advisory: CVE-2026-73615
Aliases: GHSA-9v4f-j8cv-fhxw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73615
Type: osv

## Details
Network-AI versions before 5.15.1 contain a security matcher bypass vulnerability where SandboxPolicy evaluates raw command strings with quotes preserved while the executor tokenizes commands by stripping quotes before execution. Attackers can craft quoted commands that evade blocklist checks and approval gates while the executor runs the identical unquoted dangerous argv.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73615.json
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-9v4f-j8cv-fhxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-73615
- https://www.vulncheck.com/advisories/network-ai-sandboxpolicy-before-blocklist-bypass-via-quote-mismatch
