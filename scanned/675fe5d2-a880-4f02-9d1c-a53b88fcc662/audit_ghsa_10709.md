# [C] OAuth2 Proxy has an Authentication Bypass via X-Forwarded-Uri Header Spoofing

## Summary
Severity: Critical
Advisory: GHSA-7x63-xv5r-3p2x
CVE: CVE-2026-40575
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-7x63-xv5r-3p2x
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy/v7` — affected >=7.5.0 <7.15.2

## Details
### Impact

A configuration-dependent authentication bypass exists in OAuth2 Proxy.

Deployments are affected when all of the following are true:

* OAuth2 Proxy is configured with `--reverse-proxy`
* and at least one rule is defined with `--skip_auth_routes` or the legacy `--skip-auth-regex`

OAuth2 Proxy may trust a client-supplied `X-Forwarded-Uri` header when `--reverse-proxy` is enabled and `--skip-auth-route` or `--skip-auth-regex` is configured. An attacker can spoof this header so OAuth2 Proxy evaluates authentication and skip-auth rules against a different path than the one actually sent to the upstream application.

This can result in an unauthenticated remote attacker bypassing authentication and accessing protected routes without a valid session.


### Patches
This issue is addressed as part of the newly introduced `--trusted-proxy-ip` flag in `v7.15.2`. If you leave it unset, OAuth2 Proxy will **continue to trust ALL** source IPs (0.0.0.0/0) for backwards compatibility, which means a client may still be able to spoof forwarded headers. Therefore after upgrading we urge you to use the new `--trusted-proxy-ip` flag to set the IPs or CIDR ranges of the reverse proxies that are allowed to send `X-Forwarded-*` headers and furthermore implement the mitigation steps outlined below to properly configure your load balancer infrastructure.

### Mitigation

- Strip any client-provided `X-Forwarded-Uri` header at the reverse proxy or load balancer level
- Explicitly overwrite `X-Forwarded-Uri` with the actual request URI before forwarding requests to OAuth2 Proxy

  Example nginx mitigation for the auth subrequest:
  ```
    location /internal-auth/ {
      internal; # Ensure external users can't access this path
  
      # Make sure the OAuth2 Proxy knows where the original request came from.
      proxy_set_header Host       $host;
      proxy_set_header X-Real-IP  $remote_addr;
      # set the value to the actual $request_uri and therefore strip any user provided X-Forwarded-Uri
      proxy_set_header X-Forwarded-Uri $request_uri;
  
      proxy_pass http://oauth2-proxy:4180/;
    }
  ```
- Restrict direct client access to OAuth2 Proxy so it can only be reached through a trusted reverse proxy
- Remove or narrow `--skip-auth-route` / `--skip-auth-regex` rules where possible

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-7x63-xv5r-3p2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-40575
- https://access.redhat.com/security/cve/CVE-2026-40575
- https://bugzilla.redhat.com/show_bug.cgi?id=2460449
- https://github.com/oauth2-proxy/oauth2-proxy
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40575.json
