# [H] Open WebUI: Path traversal / SSRF in terminal server proxy via encoded path traversal

## Summary
Severity: High
Advisory: GHSA-r2wg-2mcr-66rv
CVE: CVE-2026-54017
CWE: CWE-22, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-r2wg-2mcr-66rv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
### Summary

The terminal-server reverse proxy in `backend/open_webui/routers/terminals.py` does not fully confine the user-controlled `path` segment before forwarding it to an admin-configured terminal server. An authenticated user who has been granted access to a terminal server can craft `path` values containing encoded `../` traversal sequences that escape the intended path (or policy) scope on that server, reaching unintended endpoints and files on the terminal-server host. Where the terminal server fans requests out to internal services, this also gives SSRF-style reach into those services.

This is a separate code path from the `/api/v1/retrieval/process/web` SSRF (GHSA-c6xv-rcvw-v685), with its own input. Two distinct vectors are consolidated here:

1. Raw path forwarding / single-encoded traversal (original report).
2. A bypass of the subsequently-added `_sanitize_proxy_path` mitigation using double-encoded dots (`%252e%252e`).

The attacker-controlled input is the request `path`, supplied by the non-admin user, not anything an administrator configures, so this is not an admin-trust / Rule-9 situation.

### Affected code

The proxy route forwards an arbitrary trailing path to the configured terminal server:

```python
# routers/terminals.py
@router.api_route('/{server_id}/{path:path}', methods=PROXY_METHODS)
async def proxy_terminal(server_id, path, request, user=Depends(get_verified_user)):
    ...
    safe_path = _sanitize_proxy_path(path)
    if safe_path is None:
        return JSONResponse({'error': 'Invalid path'}, status_code=400)
    target_url = f'{base_url}/{safe_path}'
    policy_id = connection.get('policy_id')
    if policy_id:
        target_url = f'{base_url}/p/{policy_id}/{safe_path}'
```

Access requires `has_connection_access(user, connection, ...)`, i.e. a non-admin user the administrator has granted to that terminal server.

### Vector 1 — single-encoded traversal (original)

The path was originally concatenated to the base URL with no sanitization (`target_url = f"{base_url}/{path}"`), so single-encoded traversal escaped the intended scope:

```
GET /api/v1/terminals/server1/..%2F..%2F..%2Finternal-api/secrets
# proxied to: {base_url}/../../../internal-api/secrets
```

This vector is closed at HEAD: `_sanitize_proxy_path` now URL-decodes once, runs `posixpath.normpath`, strips leading slashes, and rejects results beginning with `..` (`unquote('..%2F..%2F') -> '../../' -> normpath -> '../..'` -> rejected).

### Vector 2 — double-encoded bypass of `_sanitize_proxy_path`

`_sanitize_proxy_path` decodes the path only once before the `..` check, so a double-encoded payload survives:

```python
def _sanitize_proxy_path(path: str) -> str | None:
    decoded = unquote(path)                 # single decode pass only
    normalized = posixpath.normpath(decoded)
    cleaned = normalized.lstrip('/')
    if cleaned.startswith('..') or cleaned == '.':
        return None
    ...
```

`unquote('%252e%252e/secret')` yields `%2e%2e/secret` (not `..`), which `normpath` leaves unchanged and which does not start with `..`, so it passes the check. The proxy then forwards `{base_url}/%2e%2e/secret`, and the upstream terminal server decodes `%2e%2e` into `..` and resolves the traversal the check was meant to prevent.

```
GET /api/v1/terminals/server1/%252e%252e/%252e%252e/sensitive-file
# passes _sanitize_proxy_path as %2e%2e/%2e%2e/sensitive-file
# upstream decodes -> ../../sensitive-file
```

The `policy_id` form (`{base_url}/p/{policy_id}/{safe_path}`) is the higher-impact target: traversal escapes the policy namespace and reaches other policies or the terminal-server root.

### Impact

An authenticated user with access to a terminal server can escape the intended path/policy scope on that server, reaching unintended endpoints and files, and, where the terminal server routes onward to internal services, reach those services. CWE-22 (Path Traversal) and CWE-918 (SSRF).

### Fix

Decode the proxy path until it is stable before normalising and checking, so no depth of encoding can smuggle a traversal sequence past the check to be re-decoded upstream:

```python
decoded = path
for _ in range(8):
    once = unquote(decoded)
    if once == decoded:
        break
    decoded = once
normalized = posixpath.normpath(decoded)
cleaned = normalized.lstrip('/')
if cleaned.startswith('..') or cleaned == '.':
    return None
```

This rejects `%2e%2e`, `%252e%252e`, `%25252e%25252e`, `..%2f..%2f`, etc., while leaving legitimate paths (including singly-encoded characters such as `%20`) intact.

### Credits

- **Tulgaaaaaaaa** — original report (terminal-proxy path SSRF / single-encoded traversal).
- **sermikr0** — double-encoded (`%252e%252e`) bypass of the `_sanitize_proxy_path` mitigation.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-r2wg-2mcr-66rv
- https://nvd.nist.gov/vuln/detail/CVE-2026-54017
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2751.yaml
- https://pypi.org/project/open-webui
