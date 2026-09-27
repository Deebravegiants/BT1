# [C] Server side template inject (SSTI) in Edgewall Genshi Template Engine

## Summary
Severity: Critical
Advisory: CVE-2026-0685
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-0685
Type: osv

## Details
Server side template inject (SSTI) in the expression evaluation component in Genshi Template Engine version 0.7.9 allows a remote attacker to achieve remote code execution (RCE) via crafted template expressions.

## References
- https://github.com/edgewall/genshi/
- https://www.kb.cert.org/vuls/id/244846
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0685.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0685
