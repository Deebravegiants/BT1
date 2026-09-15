# [C] LiteLLM has SQL Injection in Proxy API key verification

## Summary
Severity: Critical
Advisory: GHSA-r75f-5x8p-qvmc
CVE: CVE-2026-42208
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-r75f-5x8p-qvmc
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=1.81.16 <1.83.7

## Details
### Impact

A database query used during proxy API key checks mixed the caller-supplied key value into the query text instead of passing it as a separate parameter. An unauthenticated attacker could send a specially crafted `Authorization` header to any LLM API route (for example `POST /chat/completions`) and reach this query through the proxy's error-handling path.

An attacker could read data from the proxy's database and may be able to modify it, leading to unauthorised access to the proxy and the credentials it manages.

### Patches

Fixed in **`1.83.7`**. The caller-supplied value is now always passed to the database as a separate parameter. Upgrade to `1.83.7` or later.

### Workarounds

If upgrading is not immediately possible, set `disable_error_logs: true` under `general_settings`. This removes the path through which unauthenticated input reaches the vulnerable query.

### References

- Patched release: [`v1.83.7-stable`](https://github.com/BerriAI/litellm/releases/tag/v1.83.7-stable)

**Discovery Credit**: Tencent YunDing Security Lab

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-r75f-5x8p-qvmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42208
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.83.7-stable
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-42208
