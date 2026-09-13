# [M] http4k: `reverseProxy()` defaulted to substring (`Contains`) matching on `Host`; tightened to `Exact`

## Summary
Severity: Medium
Advisory: GHSA-jrpc-7vxp-69p6
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jrpc-7vxp-69p6
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-core` — affected >=6.0.0.0 <6.49.0.0
- Maven: `org.http4k:http4k-core` — affected >=5.0.0.0 <5.42.0.0
- Maven: `org.http4k:http4k-core` — affected >=0 <4.51.0.0

## Details
### Impact

`reverseProxy()` and `reverseProxyRouting()` matched configured vhosts by substring on the `Host` header (`Contains` matcher) by default. The intended use of these functions in http4k is **outbound dispatch** (e.g. matching AWS service subdomains, per the `Contains` docstring) and **test-time composition** of fake backend networks. In either of those contexts the matched `Host` is set by the calling application, not by an external attacker, so the loose match has no exploit surface.

If, however, `reverseProxy()` was deployed as a public-facing inbound HTTP handler — which the function technically supports but is not the documented intent — an external attacker could send `Host: admin.evil.com` and reach a vhost configured as `admin`, bypassing routing-based authorization.

The `Contains` matcher's docstring explicitly documented this loose behaviour, but because `Contains` was the default, callers who never read the matcher docs would still get the loose behaviour.

**Who is affected:** only deployments using `reverseProxy()` / `reverseProxyRouting()` as a public-facing inbound HTTP handler with two or more configured virtual hosts. The intended outbound / test-time usage is unaffected. If you *did* deploy `reverseProxy()` inbound and rely on multi-vhost routing for authorization, treat upgrade as urgent.

### Patches

| Line | Fixed in | Edition |
|------|----------|---------|
| v6.x (Community) | **6.49.0.0** | Community |
| v5.x (LTS) | **5.42.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) (if `reverseProxy()` is present in your v5.x line) |
| v4.x (LTS) | **4.51.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) (if `reverseProxy()` is present in your v4.x line) |

The fix changes the default matcher to `Exact`. Existing callers that genuinely need substring matching (e.g. AWS subdomain dispatch) must explicitly pass `matcher = Contains`.

### Workarounds

For deployments that cannot upgrade immediately: wrap your `reverseProxy()` with a host-allow-list filter that requires an exact match against expected vhost names before delegating.

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-jrpc-7vxp-69p6
- https://github.com/http4k/http4k/commit/0121b05537
- https://github.com/http4k/http4k/commit/54c6385615
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/releases/tag/6.49.0.0
