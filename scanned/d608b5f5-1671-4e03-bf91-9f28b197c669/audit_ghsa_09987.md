# [H] Heimdall has an authorization bypass via path normalization mismatch

## Summary
Severity: High
Advisory: GHSA-3q34-rx83-r6mq
CVE: CVE-2026-42274
CWE: CWE-35, CWE-436
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-3q34-rx83-r6mq
Type: github-advisory

## Affected
- Go: `github.com/dadrus/heimdall` — affected >=0 <0.17.14

## Details
### Summary

Heimdall performs rule matching on the raw (non-normalized) request path, while downstream components may normalize dot-segments according to [RFC 3986, Section 6.2.2.3](https://www.rfc-editor.org/rfc/rfc3986#section-6.2.2.3). This discrepancy can result in heimdall authorizing a request for one path (e.g., `/user/../admin`, or URL-encoded variants such as `/user/%2e%2e/admin` or `/user/%2e%2e%2fadmin`. The latter would require the `allow_encoded_slashes` option to be set to `on` or `no_decode`.) while the downstream ultimately processes a different, normalized path (`/admin`).

### Details

This vulnerability can be exploited by an adversary if rule matching is performed using free (named or unnamed) wildcards without further constraints, as shown in the example snippets below.

```yaml
id: rule-1
match:
  routes:
    - path: /user/**
execute: # configured to require authentication and authorization
  # ...
```

```yaml
id: rule-2
match:
  routes:
    - path: /public/**
execute: # configured to allow anonymous access
  # ...
```

If an adversary sends a request to `/public/../user/whatever`, rule-2 will be matched and executed. The downstream service may, however, normalize the request path and interpret it as `/user/whatever`.

### Impact

Bypass of access control policies enforced by heimdall may lead to the following consequences:

* Access to or modification of data that should be restricted
* Invocation of functionality that is expected to require authentication or authorization
* In certain configurations, escalation of privileges depending on the exposed functionality

### Workarounds

* Normalize HTTP paths or reject HTTP paths containing relative path expressions in the layers in front of Heimdall - this is good practice anyway. Some proxies do that by default, such as Traefik; others, such as Envoy, require additional configuration (for Envoy see [`normalize_path`](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-normalize-path)).
* Include the ID of the rule expected to be executed in the JWT issued by heimdall and check that value in the consuming project's service.

## References
- https://github.com/dadrus/heimdall/security/advisories/GHSA-3q34-rx83-r6mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42274
- https://github.com/dadrus/heimdall/pull/3209
- https://github.com/dadrus/heimdall/commit/b5dfa484b7a8c2ce6d8691c026f9da867719947a
- https://github.com/dadrus/heimdall
- https://github.com/dadrus/heimdall/releases/tag/v0.17.14
- https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-normalize-path
- https://www.rfc-editor.org/rfc/rfc3986#section-6.2.2.3
