# [M] Solon Vulnerable to Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-m63q-4hr8-5r5h
CVE: CVE-2025-46096
CWE: CWE-22, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-m63q-4hr8-5r5h
Type: github-advisory

## Affected
- Maven: `org.noear:solon-faas-luffy` — affected >=3.1.2 <3.2.0

## Details
Directory Traversal vulnerability in solon v.3.1.2 allows a remote attacker to conduct XSS attacks via the solon-faas-luffy component

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-46096
- https://github.com/opensolon/solon/issues/357
- https://github.com/opensolon/solon/commit/49a3bf95fdcf050829843004b65a2b336ca6ddff
- https://gist.github.com/yaoyao-cool/1b7d80930fea88b6fd4839646cedc437
- https://github.com/opensolon/solon
