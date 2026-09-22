# [H] Tesla: Authorization header leaks on cross-origin redirect via case-sensitive filtering

## Summary
Severity: High
Advisory: GHSA-9m9w-gxf7-rh8m
CVE: CVE-2026-48595
CWE: CWE-178
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-9m9w-gxf7-rh8m
Type: github-advisory

## Affected
- Hex: `tesla` — affected >=0.6.0 <1.18.3

## Details
### Summary

`Tesla.Middleware.FollowRedirects` is meant to strip the `Authorization` header when following a cross-origin redirect, but performs the check with a case-sensitive comparison against the lowercase string `"authorization"`. Because Tesla preserves header keys exactly as supplied by the caller, any application that sets the header with its RFC 7235 canonical casing (`"Authorization"`) bypasses the filter entirely, leaking bearer tokens or other credentials to whatever origin the redirect points at.

### Details

The filter list in `lib/tesla/middleware/follow_redirects.ex` is defined as `@filter_headers ["authorization", "host"]` and the membership check `k not in @filter_headers` compares the raw key string without case normalization. HTTP header names are case-insensitive per RFC 7230, but Tesla stores them verbatim. A header tuple `{"Authorization", "Bearer …"}` does not match `"authorization"`, so it passes through the filter and is forwarded to the redirect destination unchecked. The same defect applies to the `"Host"` entry.

An attacker who can control a `Location:` response seen by the victim client (their own endpoint, a redirect-open service, or a compromised upstream) receives the credential on the cross-origin follow. No special configuration is required beyond the victim using the standard header casing.

### PoC

1. Configure a Tesla client with `Tesla.Middleware.FollowRedirects` and set the `Authorization` header using canonical casing (`{"Authorization", "Bearer <token>"}`).
2. Make a request to an endpoint that returns a `302` redirect to a different origin.
3. Observe that the `Authorization` header with its value is present in the request delivered to the redirect destination.

### Impact

High severity (CVSS v4.0: 8.2). Any application using `tesla` 1.4.0 through 1.18.2 with `Tesla.Middleware.FollowRedirects` and a non-lowercase `Authorization` header is affected. The workaround is to use all-lowercase `"authorization"` as the header key until upgrading to 1.18.3.

### Workarounds

Normalize all header keys to lowercase before passing them to Tesla. Use `"authorization"` instead of `"Authorization"` when setting headers via `Tesla.put_header/3` or `Tesla.Middleware.Headers`.

### Resources

* Introduction commit: https://github.com/elixir-tesla/tesla/commit/2d937d5813d7cda5cd726f41824985fb655c920f
* Patch commit: https://github.com/elixir-tesla/tesla/commit/db963dba67651b9abd1fc420a1d9679cf6efe182

## References
- https://github.com/elixir-tesla/tesla/security/advisories/GHSA-9m9w-gxf7-rh8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-48595
- https://github.com/elixir-tesla/tesla/commit/db963dba67651b9abd1fc420a1d9679cf6efe182
- https://cna.erlef.org/cves/CVE-2026-48595.html
- https://github.com/elixir-tesla/tesla
- https://osv.dev/vulnerability/EEF-CVE-2026-48595
