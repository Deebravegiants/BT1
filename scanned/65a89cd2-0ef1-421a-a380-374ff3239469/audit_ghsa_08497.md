# [H] pgAdmin 4 contains local file inclusion (LFI) and server-side request forgery (SSRF) vulnerabilities

## Summary
Severity: High
Advisory: GHSA-p58c-q354-6c4f
CVE: CVE-2026-7817
CWE: CWE-552
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-p58c-q354-6c4f
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
Local file inclusion (LFI) and server-side request forgery (SSRF) vulnerabilities in pgAdmin 4 LLM API configuration endpoints.

User-supplied api_key_file and api_url preferences were passed to the LLM provider clients without validation. An authenticated user could read arbitrary server-side files by pointing api_key_file at any path readable by the pgAdmin process, or coerce pgAdmin into making requests to internal targets (e.g. cloud metadata services such as 169.254.169.254) by setting api_url, exploiting the chat path and model-list endpoints.

Fix restricts api_key_file to the user's private storage (server mode) or home directory (desktop mode), enforces a printable-ASCII key shape and a 1024-byte read cap, and gates api_url against a configurable allow-list (config.ALLOWED_LLM_API_URLS) at every entry point.

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7817
- https://github.com/pgadmin-org/pgadmin4/issues/9900
- https://github.com/pgadmin-org/pgadmin4/commit/24485fe96
- https://github.com/pgadmin-org/pgadmin4
