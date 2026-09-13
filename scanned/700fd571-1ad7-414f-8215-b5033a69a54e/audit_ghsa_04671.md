# [H] Crawl4AI: LLM credential exfiltration in Docker server via request base_url and env: token resolution

## Summary
Severity: High
Advisory: GHSA-f989-c77f-r2cq
CWE: CWE-200, CWE-522, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-f989-c77f-r2cq
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.8.8

## Details
### Summary

The Docker API server let a request control where LLM calls were sent and which environment variable an LLM token resolved from. Both could be abused to exfiltrate server-held secrets. The Docker API is unauthenticated by default.

### Vector 1 - attacker base_url

`/md`, `/llm`, and `/llm/job` accepted a `base_url` in the request and used it as the LLM endpoint while still attaching the server's configured provider API key. An attacker set `base_url` to a server they control and received the provider key (and any provider keys the server holds) in the inbound request.

### Vector 2 - arbitrary environment variable read via `env:`

`LLMConfig(api_token="env:NAME")` resolved `NAME` from the server environment with `os.getenv`. Because request bodies were deserialized into `LLMConfig` (via a crawler config / extraction strategy), an attacker could set `api_token="env:SECRET_KEY"` (or `env:REDIS_PASSWORD`, etc.) and, paired with an attacker `base_url`, exfiltrate that secret. Reading the server's `SECRET_KEY` enables forging authentication tokens.

### Impact

Disclosure of LLM provider API keys and other server secrets to an attacker-controlled endpoint; reading the JWT `SECRET_KEY` can lead to authentication bypass.

### Fix

- The LLM endpoints ignore a request-supplied `base_url`; the endpoint is always derived server-side from the provider name. The field is still accepted but no longer honored (no breaking 4xx).
- `LLMConfig` refuses `env:` resolution of protected environment-variable names (names containing SECRET/PASSWORD/PRIVATE, prefixes CRAWL4AI*/AWS_SECRET*, and SECRET_KEY/REDIS_PASSWORD/TOKEN). Normal provider keys (e.g. OPENAI_API_KEY) are unaffected.

### Workarounds

- Upgrade to the patched version.
- Enable authentication (`CRAWL4AI_API_TOKEN`).
- Do not place sensitive secrets in the server environment alongside provider keys.

### Credits

- Geo ([geo-chen](https://github.com/geo-chen)) - reported the LLM credential exfiltration via request base_url.
- Internal security audit (Crawl4AI maintainers) - the env: arbitrary-variable read.

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-f989-c77f-r2cq
- https://github.com/unclecode/crawl4ai
