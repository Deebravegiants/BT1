# [H] CVE-2025-51482

## Summary
Severity: High
Advisory: CVE-2025-51482
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51482
Type: osv

## Details
Remote Code Execution in letta.server.rest_api.routers.v1.tools.run_tool_from_source in letta-ai Letta 0.7.12 allows remote attackers to execute arbitrary Python code and system commands via crafted payloads to the /v1/tools/run endpoint, bypassing intended sandbox restrictions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51482.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51482
- https://github.com/letta-ai/letta/pull/2630
- https://github.com/letta-ai/letta
- https://www.gecko.security/blog/cve-2025-51482
