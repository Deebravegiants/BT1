# [M] frp has an authentication bypass in HTTP vhost routing when routeByHTTPUser is used for access control

## Summary
Severity: Medium
Advisory: GHSA-pq96-pwvg-vrr9
CVE: CVE-2026-40910
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-pq96-pwvg-vrr9
Type: github-advisory

## Affected
- Go: `github.com/fatedier/frp` — affected >=0.43.0 <0.68.1

## Details
### Summary
frp contains an authentication bypass in the HTTP vhost routing path when `routeByHTTPUser` is used as part of access control. In proxy-style requests, the routing logic uses the username from `Proxy-Authorization` to select the `routeByHTTPUser` backend, while the access control check uses credentials from the regular `Authorization` header. As a result, an attacker who can reach the HTTP vhost entrypoint and knows or can guess the protected `routeByHTTPUser` value may access a backend protected by `httpUser` / `httpPassword` even with an incorrect `Proxy-Authorization` password.

This issue affects deployments that explicitly use `routeByHTTPUser`. It does not affect ordinary HTTP proxies that do not use this feature.

### Details
The issue is in `pkg/util/vhost/http.go`.

In proxy-style requests using an absolute URI, the routing path extracts the username from `Proxy-Authorization` and stores it as the request `HTTPUser`, which is then used for `routeByHTTPUser` route selection.

More specifically, `injectRequestInfoToCtx()` derives the routing user from `Proxy-Authorization`, while the original `ServeHTTP()` implementation used `req.BasicAuth()` for the authentication check.

Because routing and authentication use different credential sources, a request can be routed to a protected backend based on the `Proxy-Authorization` username while the authentication check is not performed against the same credentials. This creates an authentication bypass when `routeByHTTPUser`, `httpUser`, and `httpPassword` are used together.

This is not a universal anonymous bypass for all frp HTTP proxies; it is specific to deployments that use `routeByHTTPUser` and where the target user value is known or can be inferred.

A minimal fix is to make the authentication check in proxy mode use the same credential source as route selection, i.e. to derive proxy-mode credentials from `Proxy-Authorization` consistently.

From local Git history analysis, this logic appears to have been introduced by commit `4af85da0c2c6eb981142a8fdb44f885d26cb9d08`, with the earliest containing release tag appearing to be `v0.43.0`.

### PoC
I reproduced the issue with the official `frp_0.68.0_linux_amd64.tar.gz` release binaries both locally and on an internet-reachable test server under my control.

Minimal setup:
- `frps` exposes an HTTP vhost entrypoint.
- One HTTP proxy is configured with:
  - `customDomains = ["example.test"]`
  - `routeByHTTPUser = "alice"`
  - `httpUser = "alice"`
  - `httpPassword = "secret"`
- The protected backend returns a constant marker string: `PRIVATE`.

Minimal request flow:
1. Direct unauthenticated request:
   - `curl -i --proxy '' -H 'Host: example.test' http://<FRPS_HOST>:<VHOST_HTTP_PORT>/`
   - Result: `404 Not Found`

2. Direct request with correct backend credentials:
   - `curl -i --proxy '' -u alice:secret -H 'Host: example.test' http://<FRPS_HOST>:<VHOST_HTTP_PORT>/`
   - Result: `200 OK`, body contains `PRIVATE`

3. Proxy-style request with incorrect `Proxy-Authorization`:
   - `curl -i --noproxy '' -x http://<FRPS_HOST>:<VHOST_HTTP_PORT> --proxy-user alice:wrong http://example.test/`
   - Result: `200 OK`, body contains `PRIVATE`

Observed minimal result summary:
- `DIRECT_NOAUTH -> 404`
- `DIRECT_BASICAUTH_GOOD -> 200 PRIVATE`
- `PROXY_PROXYAUTH_WRONGPASS -> 200 PRIVATE`

This was reproduced against the official binary, not only against a local source build.

### Impact
This is an authentication bypass leading to unauthorized access to a protected backend.

The practical impact depends on what service is behind the protected route. Examples include private application endpoints, internal administration panels, loopback-only local services, or development and operations interfaces.

Important boundary: if the protected backend is an `frpc` admin API that is separately protected by its own `webServer.user` / `webServer.password`, this issue only bypasses the outer vhost restriction and does not automatically bypass the inner admin authentication. In that case, the request may still reach the backend but correctly receive `401 Unauthorized` from the inner layer.

There is also a deployment-specific downstream impact path. If the bypassed backend is an `frpc` admin API without separate inner authentication, and if that `frpc` instance permits store-based proxy management, an attacker may be able to create additional plugin-based proxies through the admin API. In deployments where a `unix_domain_socket` proxy can be used to expose Docker's Unix socket, this may further expose the Docker API and potentially enable host-level command execution through Docker. This follow-on consequence depends on multiple additional deployment conditions and should be treated as a conditional downstream impact rather than the core vulnerability itself.

Because exploitation requires a deployment to explicitly use `routeByHTTPUser`, and because the attacker must know or be able to guess the target `routeByHTTPUser` value, the issue is better classified as a configuration-dependent authentication bypass rather than a default-configuration issue.

## References
- https://github.com/fatedier/frp/security/advisories/GHSA-pq96-pwvg-vrr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40910
- https://github.com/fatedier/frp
