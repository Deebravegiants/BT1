# [M] CVE-2025-63390

## Summary
Severity: Medium
Advisory: CVE-2025-63390
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-63390
Type: osv

## Details
An authentication bypass vulnerability exists in AnythingLLM v1.8.5 in via the /api/workspaces endpoint. The endpoint fails to implement proper authentication checks, allowing unauthenticated remote attackers to enumerate and retrieve detailed information about all configured workspaces. Exposed data includes: workspace identifiers (id, name, slug), AI model configurations (chatProvider, chatModel, agentProvider), system prompts (openAiPrompt), operational parameters (temperature, history length, similarity thresholds), vector search settings, chat modes, and timestamps.

## References
- https://gist.github.com/Cristliu/0897bceac5fdc2d945304b5087a84f14
- https://gist.github.com/Cristliu/ba529c99abec87102e5ef36435d02a6d
- https://github.com/Mintplex-Labs/anything-llm/issues
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63390.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63390
