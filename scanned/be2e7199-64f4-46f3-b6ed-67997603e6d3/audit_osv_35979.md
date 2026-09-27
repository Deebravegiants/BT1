# [M] Incorrect authorization in Strands Agents Tools http_request proxy credential exfiltration

## Summary
Severity: Medium
Advisory: CVE-2026-18394
Aliases: GHSA-qhw6-2h72-m84v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-18394
Type: osv

## Details
Incorrect authorization in the http_request tool in Strands Agents Tools before 0.8.2 might allow remote attackers to obtain credentials configured via HTTP_REQUEST_TOKEN_CONFIG by influencing the LLM to route requests through actor-controlled proxy infrastructure.



To remediate this issue, users should upgrade to version 0.8.2.

## References
- https://aws.amazon.com/security/security-bulletins/2026-069-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18394.json
- https://github.com/strands-agents/tools/security/advisories/GHSA-qhw6-2h72-m84v
- https://nvd.nist.gov/vuln/detail/CVE-2026-18394
- https://github.com/strands-agents/tools/releases/tag/v0.8.2
