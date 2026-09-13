# [C] n8n: Expression Sandbox Escape via Shared Builtin Tampering and Code-Printer Injection Leads to Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-86083
Aliases: GHSA-6xcw-7xm6-48c6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86083
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 1.123.76, 2.37.7, and 2.38.2, the legacy expression engine generated source text by calling the mutable global JSON.stringify while printing synthetic string literals and interpolating timezone data. An expression could replace JSON.stringify and cause later generated source to contain executable attacker-controlled code. The affected code-generation paths include packages/@n8n/expression-runtime/src/bridge/isolated-vm-bridge.ts and packages/@n8n/tournament/src/ExpressionBuilder.ts, and the issue does not affect the vm expression engine. This issue is fixed in versions 1.123.76, 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.76
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86083.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-6xcw-7xm6-48c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-86083
