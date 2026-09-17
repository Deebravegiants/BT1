# [H] Path traversal in flaskcode Devan-Kerman ARRP

## Summary
Severity: High
Advisory: GHSA-cg24-jjr5-rxmf
CVE: CVE-2024-24042
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-19
Source: https://github.com/advisories/GHSA-cg24-jjr5-rxmf
Type: github-advisory

## Affected
- Maven: `net.devtech:arrp` — affected >=0 <0.8.2

## Details
Directory Traversal vulnerability in Devan-Kerman ARRP v.0.8.1 and before allows a remote attacker to execute arbitrary code via the dumpDirect in RuntimeResourcePackImpl component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24042
- https://github.com/Devan-Kerman/ARRP/commit/7ea80db462c8bf66a0565e84fa49c1f2ecb9287b
- https://gist.github.com/apple502j/193358682885fe1a6708309ce934e4ed
- https://github.com/Devan-Kerman/ARRP
