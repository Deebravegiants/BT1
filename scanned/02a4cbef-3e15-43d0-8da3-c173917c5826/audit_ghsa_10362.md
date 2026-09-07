# [H] OAuth2 Proxy has an Authentication Bypass via Fragment Confusion in skip_auth_routes and skip_auth_regex

## Summary
Severity: High
Advisory: GHSA-pxq7-h93f-9jrg
CVE: CVE-2026-41059
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-pxq7-h93f-9jrg
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy/v7` — affected >=7.5.0 <7.15.2

## Details
### Impact

A configuration-dependent authentication bypass exists in OAuth2 Proxy.

Deployments are affected when all of the following are true:

* Use of `skip_auth_routes` or the legacy `skip_auth_regex` * Use of patterns that can be widened by attacker-controlled suffixes,    such as `^/foo/.*/bar$` causing potential exposure of `/foo/secret` * Protected upstream applications that interpret `#` as a fragment delimiter    or otherwise route the request to the protected base path

In deployments that rely on these settings, an unauthenticated attacker can send a crafted request containing a number sign in the path, including the browser-safe encoded form `%23`, so that OAuth2 Proxy matches a public allowlist rule while the backend serves a protected resource.

Deployments that do not use these skip-auth options, or that only allow exact public paths with tightly scoped method and path rules, **ARE NOT** affected.

### Patches

A fix has been implemented to normalize request paths more conservatively before skip-auth matching so fragment content does not influence allowlist decisions.

Released as part of `v7.15.2`

### Workarounds

Users who cannot upgrade immediately can reduce exposure by tightening or removing `skip_auth_routes` and `skip_auth_regex` rules, especially patterns that use broad wildcards across path segments.

Recommended mitigations:

* Replace broad rules with exact, anchored public paths and explicit HTTP methods
* Reject requests whose path contains `%23` or `#` at the ingress, load balancer, or WAF level
* Avoid placing sensitive application paths behind broad `skip_auth_routes` rules

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-pxq7-h93f-9jrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41059
- https://github.com/oauth2-proxy/oauth2-proxy
