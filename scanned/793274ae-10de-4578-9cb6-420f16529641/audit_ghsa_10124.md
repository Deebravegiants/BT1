# [C]  OAuth2 Proxy's Health Check User-Agent Matching Bypasses Authentication in auth_request Mode

## Summary
Severity: Critical
Advisory: GHSA-5hvv-m4w4-gf6v
CVE: CVE-2026-34457
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-5hvv-m4w4-gf6v
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy/v7` — affected >=0 <7.15.2
- Go: `github.com/oauth2-proxy/oauth2-proxy` — affected >=0

## Details
### Impact
A configuration-dependent authentication bypass exists in OAuth2 Proxy.

Deployments are affected when all of the following are true:

- OAuth2 Proxy is used with an `auth_request`-style integration   (for example, nginx `auth_request`)
- `--ping-user-agent` is set or `--gcp-healthchecks` is enabled

In affected configurations, OAuth2 Proxy will treat a request with the configured health check `User-Agent` value as a successful health check regardless of the requested path. This allows an unauthenticated remote attacker to bypass authentication and access protected upstream resources without completing the normal login flow.

This issue does not affect deployments that do not use `auth_request`-style subrequests, or that do not enable  `--ping-user-agent`/`--gcp-healthchecks`.

### Patches
Users should upgrade to `v7.15.2` or later once available. Deployments running versions prior to `v7.15.2` should be considered affected if they use `auth_request`-style authentication together with `--ping-user-agent` or  `--gcp-healthchecks`.

### Workarounds
Users can mitigate this issue by:

- disabling `--gcp-healthchecks`
- removing any configured `--ping-user-agent`
- ensuring the reverse proxy does not forward client-controlled `User-Agent`  headers to the OAuth2 Proxy auth subrequest
- using path-based health checks only, on dedicated health check endpoints

Example nginx mitigation for the auth subrequest:

```nginx
location = /oauth2/auth {
    internal;
    proxy_pass http://127.0.0.1:4180;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Host $host;
    # set to value that isn't the same as your configured PingUserAgent or GCPs "GoogleHC/1.0"
    proxy_set_header User-Agent "oauth2-proxy-auth-request";
}
```

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-5hvv-m4w4-gf6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34457
- https://github.com/oauth2-proxy/oauth2-proxy
- https://github.com/oauth2-proxy/oauth2-proxy/releases/tag/v7.15.2
