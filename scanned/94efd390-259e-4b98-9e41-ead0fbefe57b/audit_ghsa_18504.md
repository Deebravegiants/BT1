# [C] OAuth2-Proxy has authentication bypass in oauth2-proxy skip_auth_routes due to Query Parameter inclusion

## Summary
Severity: Critical
Advisory: GHSA-7rh7-c77v-6434
CVE: CVE-2025-54576
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-7rh7-c77v-6434
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy/v7` — affected >=0 <7.11.0

## Details
### Impact
This vulnerability affects oauth2-proxy deployments using the `skip_auth_routes` configuration option with regex patterns. The vulnerability allows attackers to bypass authentication by crafting URLs with query parameters that satisfy the configured regex patterns, potentially gaining unauthorized access to protected resources.

The issue stems from `skip_auth_routes` matching against the full request URI (path + query parameters) instead of just the path as documented. This discrepancy enables authentication bypass attacks where attackers append malicious query parameters to access protected endpoints.

Example Attack:

* Configuration: `skip_auth_routes = [ "^/foo/.*/bar$" ]`
* Intended behavior: Allow `/foo/something/bar`
* Actual vulnerability: Also allows `/foo/critical_endpoint?param=/bar`

Deployments using `skip_auth_routes` with regex patterns containing wildcards or broad matching patterns are most at risk, especially when backend services ignore unknown query parameters.


### Patches
A patch has been released with version [v7.11.0](https://github.com/oauth2-proxy/oauth2-proxy/releases/tag/v7.11.0).

### Workarounds

Immediate mitigations:

1. Review regex patterns: Audit all `skip_auth_routes` configurations for overly permissive patterns
2. Use precise patterns: Replace wildcard patterns with exact path matches where possible
3. Anchor patterns: Ensure regex patterns are properly anchored (start with `^` and end with `$`)
4. Path-only matching: Consider implementing custom validation that strips query parameters before regex matching

Example secure configuration:

```toml
# Instead of: "^/public/.*"
# Use specific paths: "^/public/assets$", "^/public/health$"
skip_auth_routes = ["^/public/assets$", "^/public/health$", "^/api/status$"]
 ```

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-7rh7-c77v-6434
- https://nvd.nist.gov/vuln/detail/CVE-2025-54576
- https://github.com/oauth2-proxy/oauth2-proxy/commit/9ffafad4b2d2f9f7668e5504565f356a7c047b77
- https://github.com/oauth2-proxy/oauth2-proxy
- https://github.com/oauth2-proxy/oauth2-proxy/blob/f4b33b64bd66ad28e9b0d63bea51837b83c00ca1/oauthproxy.go#L582-L584
- https://github.com/oauth2-proxy/oauth2-proxy/blob/f4b33b64bd66ad28e9b0d63bea51837b83c00ca1/pkg/requests/util/util.go#L37-L44
- https://github.com/oauth2-proxy/oauth2-proxy/releases/tag/v7.11.0
- https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview/#proxy-options
