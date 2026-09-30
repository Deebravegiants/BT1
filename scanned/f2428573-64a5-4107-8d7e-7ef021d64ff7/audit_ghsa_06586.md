# [H] Better Auth: Account takeover via pre-account hijacking on magic-link and email-OTP sign-in

## Summary
Severity: High
Advisory: GHSA-qq9h-g4jm-xgf3
CWE: CWE-287, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-qq9h-g4jm-xgf3
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=1.1.3 <1.6.22
- npm: `better-auth` — affected >=1.7.0-beta.0 <1.7.0-beta.10

## Details
### Am I affected

You are affected if all of the following hold:

- You run a `better-auth` version below 1.6.22, or a `1.7.0-beta` below `1.7.0-beta.10`.
- You enable the magic-link plugin or the email-OTP plugin.
- You also enable email and password sign-up with open registration.
- An account can exist at an address before its owner first signs in with the passwordless flow.

### Summary

An attacker can keep password access to a victim's account after the victim starts using it. The attack runs in three steps. First, with open registration, the attacker signs up using the victim's email and a password the attacker picks. The account stays unverified, so the attacker cannot use it yet. Later the real owner signs in with a magic link or an email OTP. That step marks the account verified, and the attacker's password now works on it.

### Details

When an account already exists for an address, magic-link verification and email-OTP sign-in both sign in to that account. They mark it verified and issue a session. Before the fix, neither one removed a password set while the account was still unverified. Neither one revoked existing sessions. So a password set before anyone proved control of the mailbox kept working after the owner proved control.

This is a pre-account-hijacking weakness. It is the same class as the OAuth advisory GHSA-g38m-r43w-p2q7, applied to the passwordless email flows. Requiring email verification does not stop it. The verification step is the exact moment that turns the planted account into a usable one.

The fix treats current proof of control over the address as authoritative. When either flow finds an account whose email was never confirmed, it now removes the password and revokes existing sessions first. Only then does it mark the account verified and issue the new session. The owner signs in as before. Only access created before the proof is removed.

### Patches

Upgrade to `better-auth` 1.6.22 or later on the stable line. On the 1.7 pre-release line, upgrade to `1.7.0-beta.10` or later. Earlier 1.7 betas, up to and including `1.7.0-beta.9`, still contain the bug.

### Workarounds

If you cannot upgrade right away, you can lower the risk in two ways. Require email verification before you accept any password on an account. Remove unverified accounts quickly, so an address cannot sit reserved for long. Both steps shrink the opening, but they do not close it. Upgrading is the real fix.

### Impact

The attacker gains lasting password access to an account the victim depends on, alongside the victim. From there the attacker can read and change the victim's data. The attacker can also reset the credentials and lock the victim out. The takeover only completes when the victim signs in through the passwordless flow. It also needs a setup that pairs that flow with open email and password sign-up.

### Credit

Reported by the Vercel security team.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-qq9h-g4jm-xgf3
- https://github.com/better-auth/better-auth/pull/10239
- https://github.com/better-auth/better-auth/commit/c06a56d83a40bbaeac12d3a8b8b67e59f92a9110
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.22
- https://github.com/better-auth/better-auth/releases/tag/v1.7.0-beta.10
