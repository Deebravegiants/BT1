# [H] Hermes WebUI < 0.51.307 Authentication Bypass via X-Forwarded-For Header Spoofing

## Summary
Severity: High
Advisory: CVE-2026-58122
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-58122
Type: osv

## Details
Hermes WebUI before 0.51.307 contains an authentication bypass vulnerability that allows unauthenticated remote attackers to circumvent local-origin IP restrictions on onboarding endpoints by supplying a spoofed X-Forwarded-For header with a loopback address. Attackers can exploit this bypass to perform server-side request forgery against internal services including cloud metadata endpoints, overwrite LLM provider configuration and API keys with attacker-controlled values, or initiate OAuth device-code flows to obtain persistent access tokens stored in auth.json.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58122.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.307
- https://nvd.nist.gov/vuln/detail/CVE-2026-58122
- https://www.vulncheck.com/advisories/hermes-webui-authentication-bypass-via-x-forwarded-for-header-spoofing
- https://github.com/nesquena/hermes-webui/pull/3758
- https://github.com/nesquena/hermes-webui/commit/70596e6993be0d4cee083c1c1a86f5e7ad5d57b7
- https://github.com/nesquena/hermes-webui
