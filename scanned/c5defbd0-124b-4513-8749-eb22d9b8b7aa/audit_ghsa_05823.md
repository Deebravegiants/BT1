# [H] Authorizer: Zero-click account takeover via OAuth identity linking to unverified email accounts

## Summary
Severity: High
Advisory: GHSA-29rf-f4vv-pvq6
CVE: CVE-2026-35511
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-29rf-f4vv-pvq6
Type: github-advisory

## Affected
- Go: `github.com/authorizerdev/authorizer` — affected >=0 <0.0.0-20260807033110-66fe488fd2a4

## Details
The OAuth callback handler links incoming OAuth identities (Google, GitHub, etc.) to existing accounts matched by email address without verifying that the existing account's email was verified by its original owner. An attacker who pre-registers with a victim's email address (without verifying it) gains persistent password-based access to the victim's account after the victim completes a normal OAuth login. Verified against HEAD (commit 73679fa).

## Root Cause

In `internal/http_handlers/oauth_callback.go`, when an OAuth login occurs for an email that already exists in the database:

Line 125: The existing user is looked up by email:

    existingUser, err := h.StorageProvider.GetUserByEmail(ctx, refs.StringValue(user.Email))

Line 164: The OAuth user object is replaced with the existing user:

    user = existingUser

Lines 173-176: The OAuth provider is appended to the existing user's signup methods:

    signupMethod := existingUser.SignupMethods
    if !strings.Contains(signupMethod, provider) {
        signupMethod = signupMethod + "," + provider
    }
    user.SignupMethods = signupMethod

Lines 179-181: If the existing account's email was NOT verified, it is automatically verified:

    if user.EmailVerifiedAt == nil {
        now := time.Now().Unix()
        user.EmailVerifiedAt = &now
    }

Line 219: The merged user is saved to the database:

    user, err = h.StorageProvider.UpdateUser(ctx, user)

At no point is the existing account's password invalidated or the owner notified that a new OAuth identity was linked.

## Attack Chain

1. Attacker signs up with `victim@company.com` using email/password. Attacker sets a known password but does NOT click the email verification link. The account exists in the database with `EmailVerifiedAt = nil`.

2. Some time later, the real owner of `victim@company.com` logs in via Google OAuth (a completely normal action).

3. The OAuth callback at line 125 finds the attacker's existing account by email.

4. At line 164, the Google OAuth identity is linked to the attacker's account.

5. At line 179-181, the email is automatically verified (the attacker never verified it, but now it's marked as verified).

6. At line 175, "google" is appended to the signup methods. The account now has both "basic_auth" and "google" as valid login methods.

7. The attacker's original password is still valid in the database. It was never cleared, changed, or invalidated.

8. The attacker logs in with `victim@company.com` and the password they originally set. They now have full access to the victim's account, including any data the victim added via their Google session.

## Why This Is Zero-Click

The victim performs no unusual action. They simply log in via their Google account, which is the expected, secure behavior. The attacker staged the account beforehand and gains access without any further interaction.

This is a classic Account Linking vulnerability (cited in OWASP authentication guidelines). The core logic flaw is a trust boundary violation. Authorizer correctly trusts that Google has verified the email address, but it incorrectly extends that trust to validate the password that was set by the unverified attacker. The attacker maintains persistent, password-based backdoor access to the victim's account, even if the victim later revokes Authorizer's OAuth access from their Google account settings. The password was set before Google was ever involved and is never invalidated by the linking process.

## Impact

- Full account takeover for any user who logs in via OAuth
- Attacker maintains persistent password-based access even after the victim changes OAuth providers
- All data the victim creates after OAuth login is accessible to the attacker
- The victim has no indication their account was pre-staged
- Affects every OAuth provider configured in Authorizer (Google, GitHub, Facebook, Apple, LinkedIn, Twitter, Discord, Twitch, Roblox, Microsoft)

## Suggested Fix

Before linking an OAuth identity to an existing account, verify that the existing account's email is already verified:

    existingUser, err := h.StorageProvider.GetUserByEmail(ctx, refs.StringValue(user.Email))
    if err == nil {
        // Account exists. Only link if email is already verified.
        if existingUser.EmailVerifiedAt == nil {
            // Email not verified by original owner. Do NOT link.
            // Either: reject the login, or create a new separate account,
            // or delete the unverified account and create a fresh one for the OAuth user.
        }
    }

Additionally, when linking a new OAuth identity, invalidate any existing password on the account or require the user to re-authenticate via the original method.

## Credit
Koda Reef

## References
- https://github.com/authorizerdev/authorizer/security/advisories/GHSA-29rf-f4vv-pvq6
- https://github.com/authorizerdev/authorizer/commit/66fe488fd2a4e7acf1e517334344d5e8f3ddd296
- https://github.com/authorizerdev/authorizer
- https://github.com/authorizerdev/authorizer/releases/tag/2.4.0-rc.16
