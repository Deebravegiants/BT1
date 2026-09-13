# [H] Cloudreve OAuth Admin.Read scope can update OneDrive storage policy credentials

## Summary
Severity: High
Advisory: GHSA-hq88-5x99-x3gf
CVE: CVE-2026-55502
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-hq88-5x99-x3gf
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.17.0
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary

Cloudreve 4.16.1 has an OAuth scope authorization bypass in the admin storage policy routes. An OAuth bearer token scoped to `Admin.Read` but not `Admin.Write` can call `POST /api/v4/admin/policy/oauth/signin` and update OneDrive storage policy credentials.

The route is inside the admin group that requires `Admin.Read`, but it does not add the local `Admin.Write` guard used by sibling policy mutation routes. Its handler persists attacker-supplied `secret` and `app_id` values into the selected OneDrive storage policy before returning an OAuth URL.

## Impact

An OAuth application that was granted only read-only admin scope can modify persistent storage backend configuration for a OneDrive policy. This can break the storage backend, replace the stored application secret and app ID, and redirect future OAuth setup for that policy to attacker-controlled application parameters. The attack crosses the intended OAuth scope boundary because `Admin.Write` is required for sibling storage policy mutation routes.

## Reproduction

Preconditions:

1. The instance has a OneDrive storage policy.
2. An admin user authorizes an OAuth client for `Admin.Read` but not `Admin.Write`.
3. The OAuth client obtains a bearer access token for that admin user.

Send the following request with that read-only admin scoped token:

```http
POST /api/v4/admin/policy/oauth/signin HTTP/1.1
Authorization: Bearer <admin OAuth token scoped to Admin.Read only>
Content-Type: application/json

{"id":1,"secret":"attacker-secret","app_id":"attacker-app-id"}
```

Expected secure result: the request is rejected with an insufficient-scope error because it changes storage policy credentials.

Actual result: the request reaches `AdminOdOAuthURL`, and `GetOauthRedirectService.GetOAuth()` persists the supplied values to the storage policy.

## Root cause

`routers/router.go` applies `RequiredScopes(types.ScopeAdminRead)` to the authenticated admin route group. Sibling policy mutation routes add local `RequiredScopes(types.ScopeAdminWrite)` guards, for example policy create, policy update, CORS creation, OAuth callback, and policy delete.

The OneDrive OAuth signin route is missing that local write-scope guard:

```go
oauth.POST("signin",
    controllers.FromJSON[adminsvc.GetOauthRedirectService](adminsvc.GetOauthRedirectParamCtx{}),
    controllers.AdminOdOAuthURL,
)
```

The handler performs a persistent write in `service/admin/policy.go`:

```go
policy.Settings.OauthRedirect = routes.MasterPolicyOAuthCallback(dep.SettingProvider().SiteURL(c)).String()
policy.SecretKey = service.Secret
policy.BucketName = service.AppID
policy, err = storagePolicyClient.Upsert(c, policy)
```

The request fields `secret` and `app_id` come directly from the caller.

## PoC evidence

A focused scope test confirmed that a request context with only `Admin.Read` fails `CheckScope(c, types.ScopeAdminWrite)`, while `Admin.Write` implies `Admin.Read`. Therefore write routes must add `RequiredScopes(types.ScopeAdminWrite)` explicitly. The vulnerable route does not do so, and the handler writes the policy fields shown above.

## Remediation

Add `middleware.RequiredScopes(types.ScopeAdminWrite)` to `oauth.POST("signin", ...)` before the JSON handler. Consider auditing other admin test routes that perform outbound network or mail actions under only `Admin.Read`, but this persistent credential update should be fixed first.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-hq88-5x99-x3gf
- https://github.com/cloudreve/cloudreve/commit/9e9fb43e7288924cca052e5fdbb70d5365ef1ede
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.17.0
