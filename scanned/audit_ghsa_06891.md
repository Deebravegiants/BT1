# [H] Cloudreve: OAuth access tokens bypass scope enforcement due to missing client_id claim

## Summary
Severity: High
Advisory: GHSA-vgj4-345g-jcf8
CVE: CVE-2026-54560
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-vgj4-345g-jcf8
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=4.0.0-20260114075425-bc6845bd742c <4.0.0-20260606015557-ed20843dc3df

## Details
## Summary

  Cloudreve's OAuth access tokens can bypass OAuth scope enforcement.

  This does not appear to be the intended design. The documentation describes OAuth client permissions/scopes, the API
  has an insufficient-scope error code, and the code comments say `RequiredScopes(...)` should verify scopes when a
  token has scopes, while skipping checks only for non-scoped session-based authentication.

  However, OAuth access tokens are issued without the OAuth `client_id` claim. Later, the JWT verifier only loads scopes
  into the request context when `claims.ClientID != ""`. Because the OAuth access token has no `client_id`, its scopes
  are not loaded, and `RequiredScopes(...)` treats the request like a non-scoped first-party/session token and skips
  scope checks.

  As a result, a low-scope OAuth access token, for example one granted only `openid`, can call APIs requiring higher
  scopes such as file, share, workflow, user setting, WebDAV account, and potentially admin scopes when the authorizing
  user is an administrator.

  ## Why this seems unintended

  Cloudreve appears to have an explicit OAuth scope model:

  1. The official docs describe OAuth client permissions/scopes and require the authorization request to include
  requested scopes.
  2. The API error code list includes an OAuth insufficient-scope error.
  3. `RequiredScopes(...)` is used across sensitive API groups such as files, shares, workflows, user settings, WebDAV
  devices, and admin APIs.
  4. The middleware comment says scope checks are skipped only when `hasScopes` is false, for example session-based
  authentication.
  5. Default OAuth clients created during migration explicitly list scopes such as `Files.Write`, `Workflow.Write`, and
  `Shares.Write`.

  This suggests the intended design is:
  - First-party/session tokens may be non-scoped and skip OAuth scope checks.
  - OAuth access tokens should carry scope metadata and be checked against `RequiredScopes(...)`.

  The current implementation makes OAuth access tokens fall into the first category by mistake.

  ## Affected code

  In the OAuth authorization code exchange, Cloudreve passes both `ClientID` and `Scopes` into token issuance:

  ```go
  token, err := tokenAuth.Issue(c, &auth.IssueTokenArgs{
      User:               user,
      ClientID:           s.ClientID,
      Scopes:             authCode.Scopes,
      RefreshTTLOverride: refreshTTLOverride,
  })

  Location:

  - service/oauth/oauth.go

  In Issue(...), the access token includes Scopes but does not include ClientID:

  accessToken, err := jwt.NewWithClaims(jwt.SigningMethodHS256, Claims{
      TokenType: TokenTypeAccess,
      RegisteredClaims: jwt.RegisteredClaims{
          Subject:   uidEncoded,
          NotBefore: jwt.NewNumericDate(issueDate),
          ExpiresAt: jwt.NewNumericDate(accessTokenExpired),
      },
      Scopes: args.Scopes,
  }).SignedString(t.secret)

  By contrast, the refresh token does include both:

  Scopes:   args.Scopes,
  ClientID: args.ClientID,

  Location:

  - pkg/auth/jwt.go

  During request authentication, scopes are only inserted into request context if ClientID is present:

  if claims.ClientID != "" {
      util.WithValue(c, ScopeContextKey{}, claims.Scopes)
  }

  Location:

  - pkg/auth/jwt.go

  Then CheckScope(...) skips scope enforcement if no scopes are present in context:

  hasScopes, tokenScopes := GetScopesFromContext(c)
  if !hasScopes {
      return nil
  }

  Location:

  - pkg/auth/jwt.go

  RequiredScopes(...) relies on this check:

  if err := auth.CheckScope(c, requiredScopes...); err != nil {
      c.JSON(200, serializer.Err(c, err))
      c.Abort()
      return
  }

  Location:

  - middleware/auth.go

  Sensitive route groups protected by RequiredScopes(...) include:

  - Files: Files.Read / Files.Write
  - Shares: Shares.Read / Shares.Write
  - Workflows: Workflow.Read / Workflow.Write
  - User settings and security info
  - WebDAV device/account management
  - Admin APIs: Admin.Read / Admin.Write

  Location:

  - routers/router.go

  ## Reproduction steps

  1. Create or use an OAuth client with a low-privilege scope, for example only openid.
  2. Complete the OAuth authorization code flow for a normal user with:

  scope=openid

  3. Exchange the authorization code via:

  POST /api/v4/session/oauth/token

  4. Decode the returned access token.

  Expected token metadata should preserve enough OAuth client/scope context for later enforcement.

  Actual behavior:

  - The access token contains the requested scopes.
  - The access token does not contain client_id.

  5. Use the returned token as a bearer token:

  Authorization: Bearer <access_token>

  6. Call an API that requires a scope not granted to the OAuth app, for example an endpoint requiring Files.Read,
     Files.Write, UserInfo.Write, or DavAccount.Write.

  Expected result:

  - The request should fail with an insufficient-scope error.

  Actual result:

  - The scope check is skipped because no scopes were inserted into the request context.
  - The request is processed as that user.

  If the authorizing user is an administrator, the same issue can affect admin APIs requiring Admin.Read or Admin.Write,
  because the request still runs as the admin user and the admin identity check can pass while the OAuth scope check is
  skipped.

  ## Impact

  This is not an anonymous authentication bypass. The attacker still needs a valid OAuth access token for a real user.

  The impact is an OAuth consent/scope boundary bypass:

  - A third-party OAuth app can request a minimal scope such as openid.
  - After the user authorizes it, the app receives an access token.
  - That token can be used as a broader bearer token for the same user's Cloudreve account, despite not being granted
    the required scopes.

  For normal users, this may allow access to or modification of files, shares, workflows, user settings, and WebDAV
  account/device settings depending on available APIs.

  For administrator users, it may allow access to admin-scoped functionality without the OAuth app being granted
  Admin.Read or Admin.Write.

  ## Suggested fix

  1. Include ClientID: args.ClientID in access token claims when issuing OAuth access tokens:

  accessToken, err := jwt.NewWithClaims(jwt.SigningMethodHS256, Claims{
      TokenType: TokenTypeAccess,
      RegisteredClaims: jwt.RegisteredClaims{
          Subject:   uidEncoded,
          NotBefore: jwt.NewNumericDate(issueDate),
          ExpiresAt: jwt.NewNumericDate(accessTokenExpired),
      },
      Scopes:   args.Scopes,
      ClientID: args.ClientID,
  }).SignedString(t.secret)

  2. Consider making scope handling fail closed for OAuth tokens with malformed or inconsistent OAuth metadata.
  3. Add regression tests for an OAuth access token granted only openid attempting to call APIs requiring:
      - Files.Read
      - Files.Write
      - UserInfo.Write
      - DavAccount.Write
      - Admin.Read
      - Admin.Write

  Each should fail with an insufficient-scope error unless the corresponding scope was granted.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-vgj4-345g-jcf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-54560
- https://github.com/cloudreve/cloudreve/commit/ed20843dc3df20a25fcaf6b538647e11c4d68d87
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.16.1
