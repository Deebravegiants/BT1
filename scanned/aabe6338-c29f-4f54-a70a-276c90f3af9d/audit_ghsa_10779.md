# [C] OpenViking: Unauthenticated remote bot control via OpenAPI HTTP routes

## Summary
Severity: Critical
Advisory: GHSA-jgq2-vq69-gr6h
CVE: CVE-2026-40525
CWE: CWE-636
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-jgq2-vq69-gr6h
Type: github-advisory

## Affected
- PyPI: `openviking` — affected >=0 <0.3.9

## Details
OpenViking prior to commit c7bb167 contains an authentication bypass vulnerability in the VikingBot OpenAPI HTTP route surface where the authentication check fails open when the api_key configuration value is unset or empty. Remote attackers with network access to the exposed service can invoke privileged bot-control functionality without providing a valid X-API-Key header, including submitting attacker-controlled prompts, creating or using bot sessions, and accessing downstream tools, integrations, secrets, or data accessible to the bot.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40525
- https://github.com/volcengine/OpenViking/pull/1447
- https://github.com/volcengine/OpenViking/commit/c7bb1676f4d037609f041bf39e4e2bd52e8f9820
- https://github.com/volcengine/OpenViking
- https://github.com/volcengine/OpenViking/releases/tag/v0.3.9
- https://www.vulncheck.com/advisories/openviking-authentication-bypass-via-vikingbot-openapi
