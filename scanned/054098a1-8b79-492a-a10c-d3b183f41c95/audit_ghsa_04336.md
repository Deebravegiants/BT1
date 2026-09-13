# [M] Nezha Monitoring: OAuth2 Redirect URL — Host Header Injection

## Summary
Severity: Medium
Advisory: GHSA-9rc6-8cjv-rcvx
CVE: CVE-2026-53523
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-9rc6-8cjv-rcvx
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.0.0 <2.2.0

## Details
## 1. Description

The `getRedirectURL` function in `oauth2.go:22-29` constructs the OAuth2 callback URL by concatenating the request's `Host` header with a fixed path, with **zero validation** of the Host header:

```go
func getRedirectURL(c *gin.Context) string {
    scheme := "http://"
    referer := c.Request.Referer()
    if forwardedProto := c.Request.Header.Get("X-Forwarded-Proto"); forwardedProto == "https" || strings.HasPrefix(referer, "https://") {
        scheme = "https://"
    }
    return scheme + c.Request.Host + "/api/v1/oauth2/callback"
}
```

**File:** `cmd/dashboard/controller/oauth2.go:22-29`

This function is called from `oauth2redirect()` at line 53:
```go
func oauth2redirect(c *gin.Context) (*model.Oauth2LoginResponse, error) {
    // ...
    redirectURL := getRedirectURL(c)
    o2conf := o2confRaw.Setup(redirectURL)
    // ...
    url := o2conf.AuthCodeURL(state, oauth2.AccessTypeOnline)
    return &model.Oauth2LoginResponse{Redirect: url}, nil
}
```

The `redirectURL` is passed into `o2confRaw.Setup(redirectURL)` which configures the OAuth2 `Config.RedirectURL` field (`oauth2config.go:22-33`). This `RedirectURL` is sent to the OAuth2 provider (e.g., GitHub, Google, Microsoft) as the callback endpoint. The OAuth2 provider will redirect the user's browser — along with the authorization code — to this URL after the user authenticates.

The security issue is that `c.Request.Host` is directly user-controllable via the HTTP `Host` header. An attacker who can control which Host header reaches the oauth2redirect handler can:

1. Set `Host: evil.com`
2. `getRedirectURL` returns `https://evil.com/api/v1/oauth2/callback`
3. The OAuth2 provider redirects the victim's auth code to `evil.com`
4. The attacker's server at `evil.com` captures the auth code
5. The attacker exchanges the code for an access token, binding the victim's OAuth identity to the attacker's dashboard account

The scheme detection (lines 24-27) uses `X-Forwarded-Proto` and the `Referer` header, both of which are also user-controllable in certain configurations, so the attacker can force `https://` scheme in the redirect URL.

The `oauth2callback` handler at line 129 later uses `state.RedirectURL` (which is stored in `singleton.Cache` at line 65) when calling `exchangeOpenId` at line 152. The cached `redirectURL` was set during the initial `oauth2redirect` call, tying the attack flow together.

## 2. PoC

A conceptual attack (no Docker needed):

```
Scenario: OAuth2 provider has loose redirect URI validation
          (e.g., allows wildcard subdomain matching)

1. Attacker crafts a URL to the dashboard's OAuth2 login endpoint
   with a modified Host header:

   GET /api/v1/oauth2/github HTTP/1.1
   Host: attacker-controlled.com
   X-Forwarded-Proto: https

2. The dashboard responds with a redirect to:
   https://github.com/login/oauth/authorize?client_id=...&redirect_uri=https://attacker-controlled.com/api/v1/oauth2/callback&state=...

3. Victim clicks the attacker's link → authenticates with GitHub
   → GitHub redirects to https://attacker-controlled.com/api/v1/oauth2/callback?code=AUTH_CODE&state=...

4. Attacker captures the AUTH_CODE from their server logs

5. Attacker exchanges the code at the real dashboard's
   /api/v1/oauth2/callback endpoint (using the real Host header
   this time), binding the victim's OAuth identity to their
   dashboard account
```

**Prerequisites for full exploit:**
- The victim must click the attacker's crafted link
- The OAuth2 provider must accept the attacker's domain as a valid redirect URI (some providers accept `https://*/*` or allow wildcards; others are strict)

## 3. Impact

- **Account takeover**: an attacker who intercepts the OAuth2 authorization code can bind the victim's OAuth identity (GitHub, Google, GitLab, etc.) to their own dashboard account, gaining the victim's access level and permissions
- **Privilege escalation**: if the victim is an admin, the attacker gains full administrative control over the Nezha deployment — access to all servers, credentials, and configuration
- **Persistence**: once bound, the attacker retains access even if the victim resets their password (unless they also unbind the OAuth2 identity)

The attack complexity is higher than typical Host header injection scenarios because it requires:
1. The `Host` header to reach the dashboard's handler unmodified (bypassing reverse proxy normalization)
2. The OAuth2 provider to have loose redirect URL validation
3. User interaction (the victim must authenticate)

However, the code-level vulnerability is unambiguous: the application trusts attacker-controlled input (`Host` header) for a security-critical URL that participates in the OAuth2 authorization code flow.

## 4. Remediation

1. **Validate the Host header** against a configured allowlist of known dashboard hostnames:
   ```go
   func getRedirectURL(c *gin.Context) string {
       host := c.Request.Host
       if !singleton.Conf.IsAllowedHost(host) {
           host = singleton.Conf.DashboardBaseURL // fallback
       }
       // ...
   }
   ```

2. **Pin the redirect URL** to the configured dashboard URL from `singleton.Conf` instead of deriving it from the request Host header:
   ```go
   func getRedirectURL(c *gin.Context) string {
       return singleton.Conf.DashboardBaseURL + "/api/v1/oauth2/callback"
   }
   ```

3. **Remove Host header-based URL construction** entirely — the OAuth2 redirect URL should be deterministic based on server configuration, not dynamic per-request

4. **Add Host header validation middleware** for all OAuth2-related endpoints as defense-in-depth

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-9rc6-8cjv-rcvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-53523
- https://github.com/nezhahq/nezha
