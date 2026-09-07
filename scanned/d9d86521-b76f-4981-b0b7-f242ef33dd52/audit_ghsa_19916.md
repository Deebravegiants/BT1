# [H] DB-GPT vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-3248-f932-c76p
CVE: CVE-2024-10906
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-3248-f932-c76p
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0

## Details
In version 0.6.0 of eosphoros-ai/db-gpt, the `uvicorn` app created by `dbgpt_server` uses an overly permissive instance of `CORSMiddleware` which sets the `Access-Control-Allow-Origin` to `*` for all requests. This configuration makes all endpoints exposed by the server vulnerable to Cross-Site Request Forgery (CSRF). An attacker can exploit this vulnerability to interact with any endpoints of the instance, even if the instance is not publicly exposed to the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10906
- https://github.com/eosphoros-ai/DB-GPT
- https://github.com/eosphoros-ai/DB-GPT/blob/f5de05b2636bc0628b3a92d32b22a26f88a18f2a/dbgpt/app/dbgpt_server.py#L240
- https://huntr.com/bounties/8864aca5-a342-4dab-b866-b2882ba6f160
