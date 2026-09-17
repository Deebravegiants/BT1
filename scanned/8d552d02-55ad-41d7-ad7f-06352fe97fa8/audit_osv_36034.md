# [H] Insecure direct object reference in Strands Agents Tools memory tool namespace isolation

## Summary
Severity: High
Advisory: CVE-2026-19111
Aliases: GHSA-mpxq-953j-42m4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-19111
Type: osv

## Details
Insecure direct object reference in the mongodb_memory, elasticsearch_memory, and mem0_memory tools in Amazon Strands Agents Tools before 0.8.3 might allow remote authenticated users to access, modify, or delete memories belonging to other tenants by influencing the LLM to emit tool calls with a forged namespace parameter.



To remediate this issue, users should upgrade to version 0.8.3.

## References
- https://aws.amazon.com/security/security-bulletins/2026-077-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19111.json
- https://github.com/strands-agents/tools/security/advisories/GHSA-mpxq-953j-42m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-19111
- https://pypi.org/project/strands-agents-tools/0.8.3/
