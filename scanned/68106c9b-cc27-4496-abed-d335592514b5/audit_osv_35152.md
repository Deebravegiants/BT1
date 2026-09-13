# [C] RAGFlow Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-68700
Aliases: GHSA-8xw3-v6c2-j84j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-68700
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine. In versions prior to 0.23.0, a low-privileged authenticated user (normal login account) can execute arbitrary system commands on the server host process via the frontend Canvas CodeExec component, completely bypassing sandbox isolation. This occurs because untrusted data (stdout) is parsed using eval() with no filtering or sandboxing. The intended design was to "automatically convert string results into Python objects," but this effectively executes attacker-controlled code. Additional endpoints lack access control or contain inverted permission logic, significantly expanding the attack surface and enabling chained exploitation. Version 0.23.0 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68700.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-8xw3-v6c2-j84j
- https://nvd.nist.gov/vuln/detail/CVE-2025-68700
- https://github.com/infiniflow/ragflow/commit/7a344a32f9f83529e12ca12f40f2657eb79fe811
