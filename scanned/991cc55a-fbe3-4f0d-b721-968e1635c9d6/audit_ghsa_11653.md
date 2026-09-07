# [C] Ory Oathkeeper has a path traversal authorization bypass

## Summary
Severity: Critical
Advisory: GHSA-p224-6x5r-fjpm
CVE: CVE-2026-33494
CWE: CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-p224-6x5r-fjpm
Type: github-advisory

## Affected
- Go: `github.com/ory/oathkeeper` — affected >=0 <0.40.10-0.20260320084758-8e0002140491

## Details
## Description

Ory Oathkeeper is vulnerable to an authorization bypass via HTTP path traversal. An attacker can craft a URL containing path traversal sequences (e.g. `/public/../admin/secrets`) that resolves to a protected path after normalization, but is matched against a permissive rule because the raw, un-normalized path is used during rule evaluation.

## Preconditions

Ory Oathkeeper rules are typically configured with patterns like:

```
/public/<.*>   → allow unauthenticated access
/admin/<.*>    → require authentication
```

Without path normalization, a request to `/public/../admin/secrets` is matched against the raw path `/public/../admin/secrets`. This matches the `/public/<.*>` rule, bypassing the authentication required for `/admin/secrets`. After Ory Oathkeeper permits the request, the upstream server normalizes the path and serves the protected `/admin/secrets` resource.

## Mitigation

Going forward, Ory Oathkeeper normalizes the request path before performing rule matching and before forwarding. The path `/public/../admin/secrets` is normalized to `/admin/secrets`, which correctly matches the `/admin/<.*>` rule and triggers authentication.

As an immediate mitigation, all requests reaching Oathkeeper should be normalized, as described in the section below. Oathkeeper should be upgraded to a fixed version as soon as possible.

## Defense in depth: Cleaning paths before Oathkeeper

Even after this fix, it is good practice to normalize HTTP paths in the layers in front of Oathkeeper. This provides defense in depth and protects against similar bypasses in other components. The following examples show how to achieve this with common reverse proxies and CDNs.

### Nginx

Nginx normalizes paths by default when using `proxy_pass`. Alternatively, use `$uri` (which Nginx normalizes) rather than `$request_uri` in your matching rules.

### Envoy

Enable the `normalize_path` option (available since Envoy 1.14) to normalize the path components before matching and forwarding. See the <a href="https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-normalize-path" target="_blank" rel="noopener noreferrer">Envoy docs on path normalization</a>.

### Cloudflare

Cloudflare normalizes URLs by default. In the Cloudflare dashboard, ensure **Normalize incoming URLs** is enabled under **Rules → Normalization**.
See the <a href="https://developers.cloudflare.com/rules/normalization/" target="_blank" rel="noopener noreferrer">Cloudflare URL normalization docs</a>.

## References
- https://github.com/ory/oathkeeper/security/advisories/GHSA-p224-6x5r-fjpm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33494
- https://github.com/ory/oathkeeper/commit/8e0002140491c592db41fa141dc6ad68f417e2b2
- https://github.com/ory/oathkeeper
