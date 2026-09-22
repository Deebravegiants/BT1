# [C] Prompt injection bypasses shell tool consent gate in Strands Agents Tools

## Summary
Severity: Critical
Advisory: CVE-2026-18733
Aliases: GHSA-mqvc-p852-wf8x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18733
Type: osv

## Details
A prompt injection vulnerability in the shell tool in Amazon Strands Agents Tools before 0.8.0 might allow remote actors to execute arbitrary operating system commands on the agent's host via a crafted prompt that sets the non_interactive parameter to true, bypassing the human consent gate.



To remediate this issue, users should upgrade to version 0.8.0.

## References
- https://aws.amazon.com/security/security-bulletins/2026-072-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18733.json
- https://github.com/strands-agents/tools/security/advisories/GHSA-mqvc-p852-wf8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-18733
- https://pypi.org/project/strands-agents-tools/0.8.0/
