# [H] litellm passes untrusted data to `eval` function without sanitization

## Summary
Severity: High
Advisory: GHSA-7ggm-4rjg-594w
CVE: CVE-2024-4264
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-18
Source: https://github.com/advisories/GHSA-7ggm-4rjg-594w
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0

## Details
A remote code execution (RCE) vulnerability exists in the berriai/litellm project due to improper control of the generation of code when using the `eval` function unsafely in the `litellm.get_secret()` method. Specifically, when the server utilizes Google KMS, untrusted data is passed to the `eval` function without any sanitization. Attackers can exploit this vulnerability by injecting malicious values into environment variables through the `/config/update` endpoint, which allows for the update of settings in `proxy_server_config.yaml`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4264
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/blob/main/litellm/proxy/proxy_server.py#L2104-L2108
- https://github.com/BerriAI/litellm/blob/main/litellm/proxy/proxy_server.py#L2118
- https://github.com/BerriAI/litellm/blob/main/litellm/proxy/proxy_server.py#L2509-L2517
- https://github.com/BerriAI/litellm/blob/main/litellm/proxy/proxy_server.py#L2562-L2577
- https://github.com/BerriAI/litellm/blob/main/litellm/utils.py#L9867-L9885
- https://huntr.com/bounties/a3221b0c-6e25-4295-ab0f-042997e8fc61
