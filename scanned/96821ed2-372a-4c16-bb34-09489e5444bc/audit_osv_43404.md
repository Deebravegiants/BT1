# [C] MindsDB Minds Platform v26.1.0 Unauthenticated RCE via scratchpad exec()

## Summary
Severity: Critical
Advisory: CVE-2026-73678
Aliases: GHSA-jcxw-h8ph-pxpv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73678
Type: osv

## Details
MindsDB Minds Platform version 26.1.0 and earlier contains an unauthenticated remote code execution vulnerability that allows unauthenticated attackers to execute arbitrary OS commands by submitting crafted prompts to the unprotected POST /api/v1/responses/ endpoint, which reaches the Anton agent's scratchpad tool that calls exec() on attacker-influenced Python source without sandboxing. Attackers can first configure their own LLM API key through the unauthenticated PUT /api/v1/settings/ endpoint, then POST a prompt directing the agent to invoke the scratchpad tool with arbitrary Python code, achieving full OS command execution as the user running the desktop application and enabling access to SSH keys, stored credentials, and environment secrets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73678.json
- https://github.com/mindsdb/minds-platform/security/advisories/GHSA-jcxw-h8ph-pxpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-73678
- https://www.vulncheck.com/advisories/mindsdb-minds-platform-unauthenticated-rce-via-scratchpad-exec
- https://github.com/mindsdb/minds-platform
- https://github.com/mindsdb/mindshub/security/advisories/GHSA-jcxw-h8ph-pxpv
