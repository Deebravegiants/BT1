# [H] LiteLLM Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-g26j-5385-hhw3
CVE: CVE-2024-6587
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-13
Source: https://github.com/advisories/GHSA-g26j-5385-hhw3
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.44.8

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in berriai/litellm version 1.38.10. This vulnerability allows users to specify the `api_base` parameter when making requests to `POST /chat/completions`, causing the application to send the request to the domain specified by `api_base`. This request includes the OpenAI API key. A malicious user can set the `api_base` to their own domain and intercept the OpenAI API key, leading to unauthorized access and potential misuse of the API key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6587
- https://github.com/berriai/litellm/commit/ba1912afd1b19e38d3704bb156adf887f91ae1e0
- https://github.com/berriai/litellm
- https://huntr.com/bounties/4001e1a2-7b7a-4776-a3ae-e6692ec3d997
