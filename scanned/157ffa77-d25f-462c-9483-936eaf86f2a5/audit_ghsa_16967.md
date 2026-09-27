# [C] LiteLLM has Server-Side Template Injection vulnerability in /completions endpoint

## Summary
Severity: Critical
Advisory: GHSA-46cm-pfwv-cgf8
CVE: CVE-2024-2952
CWE: CWE-76
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-46cm-pfwv-cgf8
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.34.42

## Details
BerriAI/litellm is vulnerable to Server-Side Template Injection (SSTI) via the `/completions` endpoint. The vulnerability arises from the `hf_chat_template` method processing the `chat_template` parameter from the `tokenizer_config.json` file through the Jinja template engine without proper sanitization. Attackers can exploit this by crafting malicious `tokenizer_config.json` files that execute arbitrary code on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2952
- https://github.com/BerriAI/litellm/issues/2949
- https://github.com/BerriAI/litellm/pull/2941
- https://github.com/BerriAI/litellm/commit/8a1cdc901708b07b7ff4eca20f9cb0f1f0e8d0b3
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/blob/0d803e13798db40aa7463e64a6bafaee386424f5/litellm/proxy/proxy_server.py#L2087
- https://github.com/advisories/GHSA-46cm-pfwv-cgf8
- https://github.com/pypa/advisory-database/tree/main/vulns/litellm/PYSEC-2026-387.yaml
- https://huntr.com/bounties/a9e0a164-6de0-43a4-a640-0cbfb54220a4
- https://pypi.org/project/litellm
