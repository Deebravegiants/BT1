# [H] Open WebUI's responses passthrough endpoint lacks access control authorization

## Summary
Severity: High
Advisory: GHSA-hp5m-24vp-vq2q
CVE: CVE-2026-44556
CWE: CWE-284, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-hp5m-24vp-vq2q
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
## Summary

The /responses endpoint in the OpenAI router accepts any authenticated user and forwards requests directly to upstream LLM providers without enforcing per-model access control. While the primary chat completion endpoint (generate_chat_completion) checks model ownership, group membership, and AccessGrants before allowing a request, the /responses proxy only validates that the user has a valid session via get_verified_user.

This allows any authenticated user — regardless of role or group assignment — to interact with any model configured on the instance by sending a POST request to /api/openai/responses with an arbitrary model ID.

## Impact

As per OWASP TOP 10 LLM:

- **Model Denial of Service (OWASP LLM04):** An unauthorized user can submit resource-intensive requests to expensive models (e.g., o1-pro, GPT-4o) that were explicitly restricted by the administrator. In shared deployments, this can exhaust API budgets or rate limits, causing total service disruption for all legitimate users.

- **Model Theft (OWASP LLM10):** If the instance proxies access to fine-tuned or self-hosted models, unauthorized users can freely interact with them, enabling capability extraction or model distillation without authorization.

- **Access Policy Bypass:** Administrators lose the ability to enforce cost-tier restrictions, team-based model assignments, or compliance boundaries through the existing access control system.

The endpoint is a raw passthrough proxy and does not resolve workspace model configurations (system prompts, knowledge bases, RAG pipelines). Therefore, workspace-specific confidential data is not directly exposed through this vector.

PR: https://github.com/open-webui/open-webui/pull/23481

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-hp5m-24vp-vq2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44556
- https://github.com/open-webui/open-webui/pull/23481
- https://github.com/open-webui/open-webui
