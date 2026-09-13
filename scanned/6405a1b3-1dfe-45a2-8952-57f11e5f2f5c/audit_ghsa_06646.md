# [H] datamodel-code-generator vulnerable to SSRF protection bypass via DNS rebinding

## Summary
Severity: High
Advisory: GHSA-vx7x-vcc2-c44g
CVE: CVE-2026-55391
CWE: CWE-350, CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-vx7x-vcc2-c44g
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0 <0.63.0

## Details
### Summary

`datamodel-code-generator`'s anti-SSRF guard validates the resolved IP of a fetch target once and then lets `httpx` perform its own independent DNS resolution to connect, so the validated address is never pinned. A hostname that resolves to a public IP at validation time and a private IP at connection time (DNS rebinding) bypasses the guard and reaches loopback, link-local cloud-metadata endpoints (`169.254.169.254`), and other internal services — even with the default `allow_private_network=False`. This is a server-side request forgery reachable when the tool fetches an attacker-influenced URL (remote `$ref`, or `--url`).

### Details

In `src/datamodel_code_generator/http.py`, `get_body()` calls `_validate_url_for_fetch()`, which resolves the host via `_get_ips_from_host()` (`socket.getaddrinfo`) and rejects non-global addresses:

```python
ips = _get_ips_from_host(host)            # resolution #1 (validation)
if not ips: return
if all(_is_safe_ip(ip) for ip in ips): return
raise SchemaFetchError(...)               # blocks private/link-local/reserved
```

It then connects with a separate, independent resolution:

```python
response = httpx.get(current_url, ...)    # resolution #2 (connection) -- NOT pinned to #1
```

Nothing ties the connection to the IP that passed validation. Between the two resolutions a low-TTL attacker-controlled record can flip from a public address (passes the guard) to a private one (used by the connection). The redirect-handling loop in the same function does correctly re-validate each redirect URL, so this is specifically a TOCTOU/rebinding gap in the host-to-IP check, not a redirect issue.

### PoC

Self-contained reproducer: https://gist.github.com/thegr1ffyn/c1d54dd6ff2a4c0d7d0dabe00c4985f4 
It starts a loopback HTTP server standing in for an internal target and patches `socket.getaddrinfo` to return a public IP on the guard's lookup and `127.0.0.1` on httpx's  the standard deterministic way to demonstrate this TOCTOU class (the real-world trigger is a low-TTL rebinding DNS record the attacker controls). 

Reachability in normal use: the attacker registers a rebinding hostname and gets the tool to fetch `http://that-host/schema.json` either via `--url` or via a remote `$ref` in a supplied schema (remote refs are fetched on the default configuration).

### Impact

Server-side request forgery (CWE-918) via a time-of-check/time-of-use resolution gap (CWE-367). Any service or CI pipeline that runs `datamodel-code-generator` against attacker-influenced URLs is affected, including deployments that rely on the default private-network protection. Consequences include reading cloud instance-metadata credentials (`169.254.169.254`), reaching internal-only HTTP services, and port/host probing of the internal network, the document fetched from the internal target is also parsed and can be reflected into the generated output.

### Maintainer status

Confirmed by maintainer review and regression tests. The private fix PR was merged and released in `0.63.0`: https://github.com/koxudaxi/datamodel-code-generator-ghsa-vx7x-vcc2-c44g/pull/1

Fix summary: pin the validated DNS result set during the HTTP fetch so a host cannot resolve to a safe address during validation and a different address during connection.

Release status: fixed in `0.63.0`; `0.62.0` and earlier are affected.

Validation: `uv run --group test --extra http pytest tests/test_http.py` passed locally for DNS pinning and URL-fetch regression coverage; `uv run --group fix ruff check src/datamodel_code_generator/http.py tests/test_http.py` passed.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-vx7x-vcc2-c44g
- https://github.com/koxudaxi/datamodel-code-generator/commit/25c8b7e497419eb20b230fa3318c04f9bebc5a6f
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.63.0
