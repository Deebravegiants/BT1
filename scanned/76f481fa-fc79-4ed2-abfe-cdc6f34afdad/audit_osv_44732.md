# [M] AgentScope through 2.0.7.post1 Arbitrary Directory Copy via add_skill

## Summary
Severity: Medium
Advisory: CVE-2026-85685
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85685
Type: osv

## Details
AgentScope through 2.0.7.post1 contains a path traversal vulnerability in LocalWorkspace.add_skill that copies arbitrary server directories into the agent workspace via an unconfined source path parameter. Attackers can supply any directory path in the skill_path request parameter to copy files into the skills directory, making them accessible through the workspace skill listing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85685.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85685
- https://www.vulncheck.com/advisories/agentscope-through-2.0.7-post1-arbitrary-directory-copy-via-add-skill
- https://github.com/agentscope-ai/agentscope/issues/2069
- https://github.com/agentscope-ai/agentscope
- https://github.com/agentscope-ai/agentscope/blob/v2.0.7.post1/src/agentscope/workspace/_local_workspace.py
