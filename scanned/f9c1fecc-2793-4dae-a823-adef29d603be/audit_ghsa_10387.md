# [M] pyLoad has a Session Cookie Security Downgrade via Untrusted X-Forwarded-Proto Header Spoofing (Global State Race Condition)

## Summary
Severity: Medium
Advisory: GHSA-mp82-fmj6-f22v
CVE: CVE-2026-40594
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-mp82-fmj6-f22v
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev98

## Details
## Summary

The `set_session_cookie_secure` `before_request` handler in `src/pyload/webui/app/__init__.py` reads the `X-Forwarded-Proto` header from any HTTP request without validating that the request originates from a trusted proxy, then mutates the **global** Flask configuration `SESSION_COOKIE_SECURE` on every request. Because pyLoad uses the multi-threaded Cheroot WSGI server (`request_queue_size=512`), this creates a race condition where an attacker's request can influence the `Secure` flag on other users' session cookies — either downgrading cookie security behind a TLS proxy or causing a session denial-of-service on plain HTTP deployments.

## Details

The vulnerable code is in `src/pyload/webui/app/__init__.py:75-84`:

```python
# Dynamically set SESSION_COOKIE_SECURE according to the value of X-Forwarded-Proto
# TODO: Add trusted proxy check
@app.before_request
def set_session_cookie_secure():
    x_forwarded_proto = flask.request.headers.get("X-Forwarded-Proto", "")
    is_secure = (
        x_forwarded_proto.split(',')[0].strip() == "https" or
        app.config["PYLOAD_API"].get_config_value("webui", "use_ssl")
    )
    flask.current_app.config['SESSION_COOKIE_SECURE'] = is_secure
```

The root cause has two components:

1. **No origin validation (CWE-346):** The `X-Forwarded-Proto` header is read from any client request. This header is only trustworthy when set by a known reverse proxy. Without `ProxyFix` middleware or a trusted proxy allowlist, any client can spoof it. The code itself acknowledges this with the TODO on line 76.

2. **Global state mutation in a multi-threaded server:** `flask.current_app.config['SESSION_COOKIE_SECURE']` is application-wide shared state. When Thread A (attacker) writes `False` to this config, Thread B (victim) may read `False` when Flask's `save_session()` runs in the after_request phase, producing a `Set-Cookie` response without the `Secure` flag.

The Cheroot WSGI server is configured with `request_queue_size=512` in `src/pyload/webui/webserver_thread.py:46`, confirming concurrent multi-threaded request processing.

No `ProxyFix` or equivalent middleware is configured anywhere in the codebase (confirmed via codebase-wide search).

## PoC

**Attack Path 1 — Cookie Security Downgrade (behind TLS-terminating proxy, `use_ssl=False`):**

An attacker with direct access to the backend (e.g., in a containerized/Kubernetes deployment) sends concurrent requests to keep `SESSION_COOKIE_SECURE` set to `False`:

```bash
# Attacker floods backend directly, bypassing TLS proxy
for i in $(seq 1 200); do
  curl -s -H 'X-Forwarded-Proto: http' http://pyload-backend:8000/ &
done

# Meanwhile, a legitimate user behind the TLS proxy receives a session cookie
# During the race window, their Set-Cookie header lacks the Secure flag
# The cookie is then vulnerable to interception over plain HTTP
```

**Attack Path 2 — Session Denial of Service (default plain HTTP deployment):**

```bash
# Attacker causes SESSION_COOKIE_SECURE=True on a plain HTTP server
for i in $(seq 1 200); do
  curl -s -H 'X-Forwarded-Proto: https' http://localhost:8000/ &
done

# Concurrent legitimate users receive Set-Cookie with Secure flag
# Browser refuses to send Secure cookies over HTTP
# Users' sessions silently break — they appear logged out
```

The second attack path works against the default configuration (`use_ssl=False`) and requires no special network position.

## Impact

- **Session cookie exposure (Attack Path 1):** When deployed behind a TLS-terminating proxy, an attacker can cause session cookies to be issued without the `Secure` flag. If the victim's browser subsequently makes an HTTP request (e.g., via a mixed-content link or downgrade attack), the session cookie is transmitted in cleartext, enabling session hijacking.

- **Session denial of service (Attack Path 2):** On default plain HTTP deployments, an attacker can continuously set `SESSION_COOKIE_SECURE=True`, causing browsers to refuse sending session cookies back to the server. This silently breaks all concurrent users' sessions with no user-visible error message, only a redirect to login.

- **No authentication required:** Both attack paths are fully unauthenticated — the `before_request` handler fires before any auth checks.

## Recommended Fix

Replace the global config mutation with per-response cookie handling, and add proxy validation:

```python
# Option A: Set Secure flag per-response instead of mutating global config
@app.after_request
def set_session_cookie_secure(response):
    # Only trust X-Forwarded-Proto if ProxyFix is configured
    is_secure = app.config["PYLOAD_API"].get_config_value("webui", "use_ssl")
    if 'Set-Cookie' in response.headers:
        # Modify cookie flags per-response, not global config
        cookies = response.headers.getlist('Set-Cookie')
        response.headers.remove('Set-Cookie')
        for cookie in cookies:
            if is_secure and 'Secure' not in cookie:
                cookie += '; Secure'
            response.headers.add('Set-Cookie', cookie)
    return response

# Option B (preferred): Use Werkzeug's ProxyFix with explicit trust
from werkzeug.middleware.proxy_fix import ProxyFix

# In App.__new__, before returning:
if trusted_proxy_count:  # from config
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=trusted_proxy_count)
# Then set SESSION_COOKIE_SECURE once at startup based on use_ssl config,
# and let ProxyFix handle X-Forwarded-Proto transparently
```

At minimum, remove the `before_request` handler entirely and set `SESSION_COOKIE_SECURE` once at startup (line 130 already does this in `_configure_session`). The dynamic per-request adjustment is the root cause of both the spoofing and the race condition.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-mp82-fmj6-f22v
- https://nvd.nist.gov/vuln/detail/CVE-2026-40594
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-125.yaml
