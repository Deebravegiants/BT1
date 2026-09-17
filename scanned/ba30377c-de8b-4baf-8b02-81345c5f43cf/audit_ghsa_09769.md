# [C] Nhost Vulnerable to Account Takeover via OAuth Email Verification Bypass

## Summary
Severity: Critical
Advisory: GHSA-6g38-8j4p-j3pr
CVE: CVE-2026-41574
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-6g38-8j4p-j3pr
Type: github-advisory

## Affected
- Go: `github.com/nhost/nhost` — affected >=0 <0.0.0-20260417112436-ec8dab3f2cf4

## Details
## Summary

Nhost automatically links an incoming OAuth identity to an existing Nhost account when the email addresses match. This is only safe when the email has been **verified by the OAuth provider**. Nhost's controller trusts a `profile.EmailVerified` boolean that is set by each provider adapter.

The vulnerability is that several provider adapters **do not correctly populate this field** they either silently drop a `verified` field the provider API actually returns (Discord), or they fall back to accepting unconfirmed emails and marking them as verified (Bitbucket). Two Microsoft providers (AzureAD, EntraID) derive the email from non-ownership-proving fields like the user principal name, then mark it verified.

The result is that an attacker can present an email they don't own to Nhost, have the OAuth identity merged into the victim's account, and receive a full authenticated session.

## Root Cause

In `services/auth/go/controller/sign_in_id_token.go`, `providerFlowSignIn()` links a new provider identity to an existing account by email match with no verification guard:

```go
// sign_in_id_token.go:267-296
func (ctrl *Controller) providerFlowSignIn(
    ctx context.Context,
    user sql.AuthUser,
    providerFound bool,
    provider string,
    providerUserID string,
    logger *slog.Logger,
) (*api.Session, *APIError) {
    if !providerFound {
        // Links attacker's provider identity to the victim's account.
        // profile.EmailVerified is NEVER checked here.
        ctrl.wf.InsertUserProvider(ctx, user.ID, provider, providerUserID, logger)
    }
    // Issues a full session  to the attacker.
    session, _ := ctrl.wf.NewSession(ctx, user, nil, logger)
    return session, nil
}
```

The controller places full trust in whatever `profile.EmailVerified` the adapter returned. The vulnerabilities below show how that trust is violated.

## Correct Implementation (For Reference)

### GitHub: `providers/github.go`

GitHub fetches `/user/emails` and reads the `verified` boolean per entry. `selectEmail()` picks only verified emails. The result is correctly mapped:

```go
selected := selectEmail(emails)   // only selects verified: true entries

return oidc.Profile{
    Email:         selected.Email,
    EmailVerified: selected.Verified,  // real boolean from GitHub API
    ...
}
```

## Vulnerable Providers

### 1. Discord: `providers/discord.go`

**The Discord `GET /users/@me` API returns a `verified` boolean field.** Per Discord's official documentation and example User Object:

```json
{
  "id": "80351110224678912",
  "username": "Nelly",
  "email": "nelly@discord.com",
  "verified": true
}
```

The Nhost struct is **missing this field**. Go's JSON decoder silently discards it:

```go
type discordUserProfile struct {
    ID            string `json:"id"`
    Username      string `json:"username"`
    Discriminator string `json:"discriminator"`
    Email         string `json:"email"`
    Locale        string `json:"locale"`
    Avatar        string `json:"avatar"`
    // MISSING: Verified bool `json:"verified"`
}
```

The adapter then sets:

```go
EmailVerified: userProfile.Email != "",  // always true when email is present
```

**Why this is exploitable:** Discord allows users to create account without verifying the email address and change their email address without immediately verifying it. After changing email, the account has `"verified": false` in the API response until the user clicks a confirmation link. An attacker can change their Discord email to the victim's address, leave it unverified, and the Nhost adapter will still present `EmailVerified: true`, because it never reads the `verified` field at all.

**Fix:**

```go
type discordUserProfile struct {
    ID            string `json:"id"`
    Username      string `json:"username"`
    Discriminator string `json:"discriminator"`
    Email         string `json:"email"`
    Verified      bool   `json:"verified"`   // add this
    Locale        string `json:"locale"`
    Avatar        string `json:"avatar"`
}

return oidc.Profile{
    Email:         userProfile.Email,
    EmailVerified: userProfile.Verified,    // use it
    ...
}
```

### 2. Bitbucket: `providers/bitbucket.go`

The Bitbucket adapter correctly queries `/user/emails` for confirmed entries, but introduces a fallback that defeats its own check:

```go
// bitbucket.go:103-132
for _, e := range emailResp.Values {
    if e.IsConfirmed {
        primaryEmail = e.Email
        break
    } else if fallbackEmail == "" {
        fallbackEmail = e.Email     // stores unconfirmed email
    }
}

if primaryEmail == "" {
    if fallbackEmail == "" {
        return oidc.Profile{}, ErrNoConfirmedBitbucketEmail
    }
    primaryEmail = fallbackEmail    //  uses unconfirmed email
}

return oidc.Profile{
    Email:         primaryEmail,
    EmailVerified: primaryEmail != "",  //  marks it true anyway
    ...
}
```

Bitbucket's `/user/emails` endpoint returns all emails, including unconfirmed ones with `"is_confirmed": false`. An attacker can add the victim's email to their Bitbucket account without confirming it, triggering the fallback path.

**Fix:**

```go
if primaryEmail == "" {
    // Remove the fallback entirely  no confirmed email means no sign-in
    return oidc.Profile{}, ErrNoConfirmedBitbucketEmail
}
```

### 3. AzureAD: `providers/azuread.go`

AzureAD derives the email through a chain of fallbacks from the userinfo response:

```go
email := userProfile.Email
if email == "" {
    email = userProfile.Prefer   // "preferred_username"  not an email ownership proof
}
if email == "" {
    email = userProfile.UPN      // User Principal Name  not an email ownership proof
}

return oidc.Profile{
    Email:         email,
    EmailVerified: email != "",  // marked verified regardless of source
    ...
}
```

`preferred_username` and UPN are internal Azure AD identity attributes. A UPN like `attacker@tenant.onmicrosoft.com` or a custom UPN set to `ceo@target-company.com` does not prove that the user controls that external email address. Yet Nhost will treat it as a verified email claim and merge identities if an existing account matches.

**Fix:** Do not fall back to `preferred_username` or UPN for account-linking email. Only use a field that Azure AD explicitly certifies as a verified external email (or use the OIDC `id_token` with the `email_verified` claim from Azure's v2 endpoint).

### 4. EntraID: `providers/entraid.go`

Same pattern as AzureAD. The EntraID adapter reads from `graph.microsoft.com/oidc/userinfo` but the struct has no `email_verified` field:

```go
type entraidUser struct {
    Sub        string `json:"sub"`
    GivenName  string `json:"givenname"`
    FamilyName string `json:"familyname"`
    Email      string `json:"email"`
    // MISSING: EmailVerified bool `json:"email_verified"`
}

return oidc.Profile{
    Email:         userProfile.Email,
    EmailVerified: userProfile.Email != "",  // unconditional
    ...
}
```

Microsoft's OIDC userinfo endpoint does include an `email_verified` claim per the OpenID Connect specification. Nhost ignores it.

**Fix:** Add `EmailVerified bool \`json:"email_verified"`` to the struct and map it correctly.

## Attack Scenario (Discord)

**Setup:** An Nhost application uses Discord OAuth. A victim has an account with `admin@target.io`.

1. Attacker opens **Discord → User Settings → Account**, changes email to `admin@target.io`, and dismisses the dialog, **without clicking the confirmation link**.
    
2. At this point Discord's API returns `"email": "admin@target.io", "verified": false` for the attacker's account.
    
3. Attacker visits the target application and clicks **Sign in with Discord**.
    
4. Nhost fetches the Discord profile. The missing `Verified` field in the struct causes the JSON decoder to drop it. The adapter sets `EmailVerified: true` because `"admin@target.io" != ""`.
    
5. Nhost finds the victim's account by email, sees no Discord provider row linked to it, and calls `InsertUserProvider` to link the attacker's Discord ID.
    
6. Nhost issues a full session for the victim's account and returns it to the attacker.
    
7. **The attacker is now authenticated as the victim.**
    

The attack is silent, the victim receives no notification and the session appears entirely legitimate.

## Defense-in-Depth Gap (Informational)

Several other providers also use `EmailVerified: email != ""`, the same logical pattern as the vulnerable ones above. However, these are **not currently exploitable** because the platforms themselves enforce email verification before returning an address in the API response:

|Provider|API Field Used|Why Not Exploitable Today|
|---|---|---|
|**Twitch**|`email` string only|Twitch requires email verification at sign-up; the API never returns an unverified email|
|**GitLab**|`email` string only|`GET /api/v4/user` only returns the confirmed primary email|
|**Facebook**|`email` via Graph API|Facebook only includes email in the response when it is confirmed|
|**Twitter**|`email` via `verify_credentials`|Twitter requires a working email address on the account|
|**Spotify**|`email` string only|Spotify enforces verification before account activation|
|**Windows Live**|`preferred` `account` email|Microsoft's Live API only surfaces confirmed addresses|
|**WorkOS**|`email` from SSO profile|Controlled by the enterprise IdP|

These providers happen to be safe due to **external platform behavior, not due to any validation in Nhost's code.** The `email != ""` shortcut is fragile:

- If any of these platforms change how their API works, Nhost silently becomes exploitable for that provider.
    
- Any developer adding a new provider in the future will likely copy the same pattern, believing it is the established convention, creating vulnerabilities in new integrations.
    

For this reason, the controller-level guard in Layer 1 of the fix below is important even beyond the four currently vulnerable providers: it makes the system safe by design regardless of what any individual adapter returns.

## Impact

- Full account takeover of any existing Nhost user.
    
- Requires no interaction from the victim.
    
- Attacker can change the account email, disable other login methods, and permanently lock out the legitimate owner.
    
- Severity escalates to Critical in applications with admin or privileged accounts.

## References
- https://github.com/nhost/nhost/security/advisories/GHSA-6g38-8j4p-j3pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41574
- https://github.com/nhost/nhost/pull/4162
- https://github.com/nhost/nhost/commit/ec8dab3f2cf46e1131ddaf893d56c37aa00380b2
- https://github.com/nhost/nhost
- https://github.com/nhost/nhost/releases/tag/auth%400.49.1
