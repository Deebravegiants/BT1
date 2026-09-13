# [H] Gogs has an Authentication Bypass via Unvalidated Reverse Proxy Headers

## Summary
Severity: High
Advisory: GHSA-w6j9-vw59-27wv
CVE: CVE-2026-25119
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-w6j9-vw59-27wv
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

When `ENABLE_REVERSE_PROXY_AUTHENTICATION` is enabled, Gogs accepts the configured authentication header (default: `X-WEBAUTH-USER`) directly from client requests without validating that the request originated from a trusted reverse proxy. Any remote attacker who can reach the Gogs service can forge this header to impersonate any user or trigger automatic account creation, completely bypassing authentication.

## Root Cause

The vulnerability exists because Gogs reads the authentication header directly from the incoming HTTP request without any verification that the header was set by a trusted reverse proxy.

### Vulnerable Code Flow

In `internal/context/auth.go` lines 206-234:

```go
func authenticatedUser(store AuthStore, ctx *macaron.Context, sess session.Store) (_ *database.User, isBasicAuth, isTokenAuth bool) {
    // ... existing auth checks ...

    if uid <= 0 {
        if conf.Auth.EnableReverseProxyAuthentication {
            // Reads header DIRECTLY from client request - NO VALIDATION!
            webAuthUser := ctx.Req.Header.Get(conf.Auth.ReverseProxyAuthenticationHeader)
            if len(webAuthUser) > 0 {
                user, err := store.GetUserByUsername(ctx.Req.Context(), webAuthUser)
                if err != nil {
                    if !database.IsErrUserNotExist(err) {
                        log.Error("Failed to get user by name: %v", err)
                        return nil, false, false
                    }

                    // Check if enabled auto-registration.
                    if conf.Auth.EnableReverseProxyAutoRegistration {
                        // Creates new user with forged username!
                        user, err = store.CreateUser(
                            ctx.Req.Context(),
                            webAuthUser,
                            gouuid.NewV4().String()+"@localhost",
                            database.CreateUserOptions{
                                Activated: true,
                            },
                        )
                        if err != nil {
                            log.Error("Failed to create user %q: %v", webAuthUser, err)
                            return nil, false, false
                        }
                    }
                }
                // Returns user as authenticated without any verification!
                return user, false, false
            }
        }
        // ... fallback to basic auth ...
    }
    // ...
}
```

The code has **zero validation** that:
1. The request came through a reverse proxy
2. The header was set by the proxy (not the client)
3. Gogs is actually behind a reverse proxy
4. The direct access to Gogs is restricted

The vulnerability occurs when:
- Gogs is publicly accessible (e.g., `0.0.0.0:3000`)
- `ENABLE_REVERSE_PROXY_AUTHENTICATION = true`

## Proof of Concept

### Prerequisites

Gogs instance with the following configuration in `custom/conf/app.ini`:

```ini
[auth]
ENABLE_REVERSE_PROXY_AUTHENTICATION = true
```

An attacker can impersonate any user including administrators:

```bash
# Become admin instantly
curl http://gogs.example.com/ -H "X-WEBAUTH-USER: <username>"
```

<img width="1835" height="1143" alt="impersonation_example" src="https://github.com/user-attachments/assets/bae60772-5eb3-4f54-9fe0-5db01595bd56" />

## Recommended Fixes

Add validation to ensure headers come from trusted sources:

```go
func authenticatedUser(store AuthStore, ctx *macaron.Context, sess session.Store) (_ *database.User, isBasicAuth, isTokenAuth bool) {
    // ... existing code ...

    if uid <= 0 {
        if conf.Auth.EnableReverseProxyAuthentication {
            // Validate request is from trusted proxy
            if !isRequestFromTrustedProxy(ctx.Req) {
                log.Warn("Reverse proxy auth header received from untrusted source: %s", ctx.RemoteAddr())
                return nil, false, false
            }

            webAuthUser := ctx.Req.Header.Get(conf.Auth.ReverseProxyAuthenticationHeader)
            // ... rest of the code ...
        }
    }
    // ...
}

// New validation function
func isRequestFromTrustedProxy(req *http.Request) bool {
    // Check if request is from localhost/trusted IPs
    remoteIP := getRemoteIP(req)

    // Only accept from localhost by default
    if remoteIP.IsLoopback() {
        return true
    }

    // Check against configured trusted proxy IPs
    for _, trustedIP := range conf.Auth.TrustedProxyIPs {
        if remoteIP.String() == trustedIP {
            return true
        }
    }

    return false
}
```

Add configuration option:

```ini
[auth]
ENABLE_REVERSE_PROXY_AUTHENTICATION = false
REVERSE_PROXY_AUTHENTICATION_HEADER = X-WEBAUTH-USER
; Comma-separated list of trusted proxy IPs (default: 127.0.0.1)
TRUSTED_PROXY_IPS = 127.0.0.1,::1
; Whether to require trusted proxy validation (recommended: true)
REQUIRE_TRUSTED_PROXY = true
```

## References

- [CWE-290: Authentication Bypass by Spoofing](https://cwe.mitre.org/data/definitions/290.html)
- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Top 10 2021 - A07: Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-w6j9-vw59-27wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-25119
- https://github.com/gogs/gogs/pull/8264
- https://github.com/gogs/gogs/commit/0089c4c8e5b8d99eb6e5c8727f8f40d765f1f58a
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
