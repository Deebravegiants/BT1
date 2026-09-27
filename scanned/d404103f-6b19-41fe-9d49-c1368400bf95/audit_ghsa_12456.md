# [H] Cookie leakage between different users in fastapi-proxy-lib

## Summary
Severity: High
Advisory: GHSA-7vwr-g6pm-9hc8
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-01
Source: https://github.com/advisories/GHSA-7vwr-g6pm-9hc8
Type: github-advisory

## Affected
- PyPI: `fastapi-proxy-lib` — affected >=0 <0.1.0

## Details
### Impact

In the implementation of version `0.0.1`, requests from different user clients are processed using a shared `httpx.AsyncClient`.

However, one oversight is that the `httpx.AsyncClient` will persistently store cookies based on the `set-cookie` response header sent by the target server and share these cookies across different user requests.

This results in a cookie leakage issue among all user clients sharing the same `httpx.AsyncClient`.

### Patches

It's fixed in `0.1.0`

### Workarounds

If you insist `0.0.1`:
- Do not use `ForwardHttpProxy` at all.
- Do not use `ReverseHttpProxy` or `ReverseWebSocketProxy` for any servers that may potentially send a `set-cookie` response.

**However, it's best to upgrade to the latest version.**

### References

fixed in [#10](https://github.com/WSH032/fastapi-proxy-lib/pull/10)

## References
- https://github.com/WSH032/fastapi-proxy-lib/security/advisories/GHSA-7vwr-g6pm-9hc8
- https://github.com/WSH032/fastapi-proxy-lib/pull/10
- https://github.com/WSH032/fastapi-proxy-lib
