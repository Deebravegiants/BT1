# [M] n8n: Domain-Restriction Bypass via Unguarded Model-Search Endpoint in OpenAI Chat Model Node

## Summary
Severity: Medium
Advisory: CVE-2026-86082
Aliases: GHSA-34ff-336r-5q23
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86082
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 1.123.76, 2.37.7, and 2.38.2, the OpenAI Chat Model node enforced credential allowed-domain restrictions for normal calls but not for the model-search dropdown. A workflow editor could set options.baseURL to an arbitrary host and make the searchModels path send the openAiApi credential there. The affected implementation is packages/@n8n/nodes-langchain/nodes/llms/LMChatOpenAi/methods/loadModels.ts, which omitted assertOpenAiCredentialAllowsUrl. This issue is fixed in versions 1.123.76, 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.76
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86082.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-34ff-336r-5q23
- https://nvd.nist.gov/vuln/detail/CVE-2026-86082
