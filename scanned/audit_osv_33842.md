# [M] CVE-2025-51472

## Summary
Severity: Medium
Advisory: CVE-2025-51472
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51472
Type: osv

## Details
Code Injection in AgentTemplate.eval_agent_config in TransformerOptimus SuperAGI 0.0.14 allows remote attackers to execute arbitrary Python code via malicious values in agent template configurations such as the goal, constraints, or instruction field, which are evaluated using eval() without validation during template loading or updates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51472.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51472
- https://github.com/TransformerOptimus/SuperAGI/pull/1461
- https://github.com/TransformerOptimus/SuperAGI
- https://www.gecko.security/blog/cve-2025-51472
