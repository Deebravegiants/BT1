# [H] LiteLLM Has a Leakage of Langfuse API Keys

## Summary
Severity: High
Advisory: GHSA-879v-fggm-vxw2
CVE: CVE-2025-0330
CWE: CWE-1230
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-879v-fggm-vxw2
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0

## Details
In berriai/litellm version v1.52.1, an issue in proxy_server.py causes the leakage of Langfuse API keys when an error occurs while parsing team settings. This vulnerability exposes sensitive information, including langfuse_secret and langfuse_public_key, which can provide full access to the Langfuse project storing all requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0330
- https://github.com/BerriAI/litellm
- https://huntr.com/bounties/661b388a-44d8-4ad5-862b-4dc5b80be30a
