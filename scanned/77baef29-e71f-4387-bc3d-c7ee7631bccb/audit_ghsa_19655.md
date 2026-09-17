# [H] LiteLLM Vulnerable to Denial of Service (DoS) via Crafted HTTP Request

## Summary
Severity: High
Advisory: GHSA-fh2c-86xm-pm2x
CVE: CVE-2024-8984
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-fh2c-86xm-pm2x
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.56.2

## Details
A Denial of Service (DoS) vulnerability exists in berriai/litellm version v1.44.5. This vulnerability can be exploited by appending characters, such as dashes (-), to the end of a multipart boundary in an HTTP request. The server continuously processes each character, leading to excessive resource consumption and rendering the service unavailable. The issue is unauthenticated and does not require any user interaction, impacting all users of the service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8984
- https://github.com/BerriAI/litellm/commit/4f49f836aa844ac9b6bfbeff27e6f6b2b9cf3f61
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/blob/8c5ff150f6142608ffe968e4e68429f978fda187/litellm/tests/test_spend_logs.py#L242
- https://huntr.com/bounties/554fc76b-3097-4223-b4cf-110b853e9355
