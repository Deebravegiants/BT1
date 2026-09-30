# [H] Contour has Lua code injection via Cookie Path Rewrite Policy

## Summary
Severity: High
Advisory: GHSA-x4mj-7f9g-29h4
CVE: CVE-2026-41246
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-x4mj-7f9g-29h4
Type: github-advisory

## Affected
- Go: `github.com/projectcontour/contour` — affected >=1.19.0 <1.31.6
- Go: `github.com/projectcontour/contour` — affected >=1.32.0 <1.32.5
- Go: `github.com/projectcontour/contour` — affected >=1.33.0 <1.33.4

## Details
### Impact

Contour's [Cookie Rewriting](https://projectcontour.io/docs/1.33/config/cookie-rewriting/) feature is vulnerable to Lua code injection. An attacker with RBAC permissions to create or modify `HTTPProxy` resources can craft a malicious value in the following fields that results in arbitrary code execution in the Envoy proxy:

- `spec.routes[].cookieRewritePolicies[].pathRewrite.value`
- `spec.routes[].services[].cookieRewritePolicies[].pathRewrite.value`

The cookie rewriting feature is internally implemented using Envoy's [HTTP Lua filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/lua_filter). User-controlled values are interpolated into Lua source code using Go `text/template` without sufficient sanitization.

The injected code only executes when processing traffic on the attacker's own route, which they already control. However, since Envoy runs as shared infrastructure, the injected code can also:

- Read Envoy's xDS client credentials from the filesystem, which could be used to read all Contour xDS configuration, including TLS certificates and private keys of other tenants.
- Cause denial of service for other tenants sharing the Envoy instance.

Other use cases of Lua filter are not vulnerable.

### Patches

The fix is available in Contour [v1.33.4](https://github.com/projectcontour/contour/releases/tag/v1.33.4), [v1.32.5](https://github.com/projectcontour/contour/releases/tag/v1.32.5), and [v1.31.6](https://github.com/projectcontour/contour/releases/tag/v1.31.6).

- v1.33.4: User-provided values are no longer interpolated into Lua code. Use of `text/template` is removed. Requires Envoy 1.35.0 or later.
- v1.32.5, v1.31.6: User-provided values are escaped before interpolation into Lua code.

### Workarounds

There are no workarounds. Users should upgrade to a patched version.

## References
- https://github.com/projectcontour/contour/security/advisories/GHSA-x4mj-7f9g-29h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41246
- https://access.redhat.com/security/cve/CVE-2026-41246
- https://bugzilla.redhat.com/show_bug.cgi?id=2461257
- https://github.com/projectcontour/contour
- https://github.com/projectcontour/contour/releases/tag/v1.31.6
- https://github.com/projectcontour/contour/releases/tag/v1.32.5
- https://github.com/projectcontour/contour/releases/tag/v1.33.4
- https://projectcontour.io/docs/1.33/config/cookie-rewriting
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41246.json
- https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/lua_filter
