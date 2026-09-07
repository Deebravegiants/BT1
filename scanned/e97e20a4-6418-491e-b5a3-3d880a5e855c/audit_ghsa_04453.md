# [M] Starlette has missing Host header validation that poisons request.url.path, bypassing path-based security checks

## Summary
Severity: Medium
Advisory: GHSA-86qp-5c8j-p5mr
CVE: CVE-2026-48710
CWE: CWE-1289, CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-86qp-5c8j-p5mr
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0 <1.0.1

## Details
### Summary
In affected versions, the HTTP `Host` request header was not validated before being used to reconstruct `request.url`. Because the routing algorithm relies on the raw HTTP path while `request.url` is rebuilt from the `Host` header, a malformed header could make `request.url.path` differ from the path that was actually requested. Middleware and endpoints that apply security restrictions based on `request.url` (rather than the raw `scope` path) could therefore be bypassed.

### Details
When a client requests `http://example.com/foo`, it sends:

```http
GET /foo HTTP/1.1
Host: example.com
```

Affected versions reconstructed the URL by concatenating `http://{host}{path}` and re-parsing the result. The `Host` value is only valid as a `uri-host [ ":" port ]` per [RFC 9112 §3.2](https://www.rfc-editor.org/rfc/rfc9112.html#section-3.2-6), where `uri-host` follows the restricted `host` grammar of [RFC 3986 §3.2.2](https://www.rfc-editor.org/rfc/rfc3986.html#section-3.2.2). When it contains characters outside that grammar - notably `/`, `?`, or `#` - those characters move the path/query/fragment boundaries during re-parsing, so the parsed `request.url.path` no longer matches the path the server actually received. For example:

```http
GET /foo HTTP/1.1
Host: example.com/abc?bar=
```

reconstructs to `http://example.com/abc?bar=/foo`, whose parsed `path` is `/abc` - even though routing used the real path `/foo`. The router still dispatches to `/foo` and the endpoint executes, but any middleware or code that reads `request.url.path` sees `/abc`, so path-based authorization checks can be bypassed.

### Impact
Any application running an affected version that relies on `request.url` (or `request.url.path`) for security-sensitive decisions is affected. The most common case is middleware that gates access to certain path prefixes based on `request.url.path`. Deployments fronted by a proxy or load balancer are mitigated only if that proxy rejects or normalizes the malformed `Host` header before forwarding and the application does not trust attacker-controlled host headers (e.g. `X-Forwarded-Host`) elsewhere.

### Mitigation
Upgrade to a patched version, which validates the `Host` header against the grammar of [RFC 9112 §3.2](https://www.rfc-editor.org/rfc/rfc9112.html#section-3.2-6) / [RFC 3986 §3.2.2](https://www.rfc-editor.org/rfc/rfc3986.html#section-3.2.2) when constructing `request.url` and falls back to `scope["server"]` for malformed values.

## References
- https://github.com/Kludex/starlette/security/advisories/GHSA-86qp-5c8j-p5mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48710
- https://github.com/Kludex/starlette/commit/764dab0dcfb9033d75442d7a359645c9f94648c6
- https://www.x41-dsec.de/lab/advisories/x41-2026-002-starlette
- https://www.secwest.net/starlette
- https://www.cve.org/CVERecord?id=CVE-2026-48710
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48710.json
- https://ostif.org/disclosing-the-badhost-vulnerability-in-starlette
- https://github.com/pypa/advisory-database/tree/main/vulns/starlette/PYSEC-2026-161.yaml
- https://github.com/Kludex/starlette
- https://bugzilla.redhat.com/show_bug.cgi?id=2481742
- https://badhost.org
- https://access.redhat.com/security/cve/CVE-2026-48710
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/errata/RHSA-2026:51357
- https://access.redhat.com/errata/RHSA-2026:44696
- https://access.redhat.com/errata/RHSA-2026:43038
- https://access.redhat.com/errata/RHSA-2026:37275
- https://access.redhat.com/errata/RHSA-2026:34532
- https://access.redhat.com/errata/RHSA-2026:34526
