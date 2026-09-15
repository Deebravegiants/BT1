# [M] LiteLLM: Authenticated SSRF and provider-credential exfiltration via unvalidated request-body routing parameters

## Summary
Severity: Medium
Advisory: CVE-2026-84377
Aliases: GHSA-3cv6-jpf6-8222
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84377
Type: osv

## Details
LiteLLM is a proxy server (AI Gateway) to call LLM APIs in OpenAI (or native) format. Prior to versions 1.88.6 and 1.96.2, any authenticated LiteLLM proxy user could redirect an outbound provider call to a destination the user controls and cause the proxy to send its configured provider credentials to that destination. Request validation in litellm/proxy/auth/auth_utils.py, litellm/proxy/common_request_processing.py, litellm/proxy/health_endpoints/_health_endpoints.py, litellm/proxy/image_endpoints/endpoints.py, and litellm/proxy/litellm_pre_call_utils.py used incomplete checks that did not cover every sensitive parameter or inspect equivalent values across nested request fields, path values, and bracket-notation form data. Routing and credential parameters including api_base, base_url, model_list, fallbacks, and litellm_credential_name could therefore be applied without clearing the operator's stored key, exposing upstream provider credentials and other configured secrets and permitting server-side requests to internal services reachable by the proxy. This issue is fixed in versions 1.88.6 and 1.96.2.

## References
- https://github.com/BerriAI/litellm/releases/tag/v1.88.6
- https://github.com/BerriAI/litellm/releases/tag/v1.96.2
- https://github.com/BerriAI/litellm/security/advisories/GHSA-3cv6-jpf6-8222
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84377.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84377
- https://github.com/BerriAI/litellm/commit/473f72e63a9777d793fbbf57194d8ec4fb97bc1b
- https://github.com/BerriAI/litellm/commit/820f247a6abba55cd87d130bef7bba7be3b29d37
- https://github.com/BerriAI/litellm/commit/c898d341c02299cf2506d0d8e84cc67953043593
- https://github.com/BerriAI/litellm/pull/36011
- https://github.com/BerriAI/litellm/pull/36314
- https://github.com/BerriAI/litellm/pull/36494
