# [C] n8n Unsafe Workflow Expression Evaluation Allows Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-5xrp-6693-jjx9
CVE: CVE-2026-1470
CWE: CWE-95
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-5xrp-6693-jjx9
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.17
- npm: `n8n` — affected >=2.0.0 <2.4.5
- npm: `n8n` — affected >=2.5.0 <2.5.1

## Details
n8n contains a critical Remote Code Execution (RCE) vulnerability in its workflow Expression evaluation system. Expressions supplied by authenticated users during workflow configuration may be evaluated in an execution context that is not sufficiently isolated from the underlying runtime.

An authenticated attacker could abuse this behavior to execute arbitrary code with the privileges of the n8n process. Successful exploitation may lead to full compromise of the affected instance, including unauthorized access to sensitive data, modification of workflows, and execution of system-level operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1470
- https://github.com/n8n-io/n8n/commit/25c4b9605b420a98d0185a4f01115122a5134d8f
- https://github.com/n8n-io/n8n/commit/30383d86139f3279a698df8d229eadfefe8627f4
- https://github.com/n8n-io/n8n/commit/aa4d1e5825829182afa0ad5b81f602638f55fa04
- https://github.com/n8n-io/n8n
- https://research.jfrog.com/vulnerabilities/n8n-expression-node-rce
