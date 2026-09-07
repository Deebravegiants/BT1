# [C] Jupiter allows attackers to execute arbitrary commands via sending a crafted RPC request

## Summary
Severity: Critical
Advisory: GHSA-6pqx-v9g4-5hc8
CVE: CVE-2023-48887
CWE: CWE-502, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-02
Source: https://github.com/advisories/GHSA-6pqx-v9g4-5hc8
Type: github-advisory

## Affected
- Maven: `org.jupiter-rpc:jupiter-rpc` — affected >=0

## Details
A deserialization vulnerability in Jupiter v1.3.1 allows attackers to execute arbitrary commands via sending a crafted RPC request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48887
- https://github.com/fengjiachun/Jupiter/issues/115
- https://github.com/fengjiachun/Jupiter
- https://github.com/welk1n/JNDI-Injection-Exploit/releases/tag/v1.0
