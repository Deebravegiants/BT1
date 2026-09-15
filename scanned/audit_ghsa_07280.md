# [H] Better Auth vulnerable to unauthorized invitation acceptance via unverified email match in organization plugin

## Summary
Severity: High
Advisory: GHSA-fmh4-wcc4-5jm3
CVE: CVE-2026-53514
CWE: CWE-287, CWE-345, CWE-441, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-fmh4-wcc4-5jm3
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.6.11

## Details
### Am I affected?

Users are affected if all of the following are true:

- Their application uses `better-auth` with the `organization` plugin (`import { organization } from "better-auth/plugins/organization"`).
- Their application enables a sign-up surface that allows arbitrary unverified email registration. Most commonly `emailAndPassword: { enabled: true }` without `requireEmailVerification: true`.
- Their application has not set `requireEmailVerificationOnInvitation: true` on the `organization()` options.
- Their application invitation distribution flow allows anyone other than the invited mailbox owner to obtain the `invitationId`. Examples: admin UI surfacing the link, copy-paste into chat, forwarded email, mail-forwarding rules at the recipient's domain, link previews logging the URL, or a custom `sendInvitationEmail` integration that sends to a non-owner channel.

If their application set `emailAndPassword: { enabled: true, requireEmailVerification: true }` so unverified rows cannot reach a usable session, they are not affected. Setting `requireEmailVerificationOnInvitation: true` closes `acceptInvitation` and `rejectInvitation`, but `getInvitation` and `listUserInvitations` remain ungated even with that flag.

Fix:

1. Upgrade to `better-auth@1.6.11` or later.
2. If developers cannot upgrade their application, see workarounds below.

### Summary

The organization plugin's `acceptInvitation` endpoint trusts an email-string equality check as proof that the session user owns the invited address. With Better Auth's stock `emailAndPassword: { enabled: true }` configuration, `requireEmailVerification` defaults to `false`, so an attacker can sign up a row keyed to `victim@target.example` (auto-signed-in, `emailVerified: false`) before the legitimate owner. When an organization admin invites that address, the attacker presents the `invitationId` and accepts the invitation, joining the organization at the invited role.

### Details

The recipient gate compares `invitation.email.toLowerCase()` to `session.user.email.toLowerCase()` and returns 403 on mismatch. The opt-in `requireEmailVerificationOnInvitation` flag adds an `emailVerified` check, but it defaults to `false` and only fires on `acceptInvitation` and `rejectInvitation`; `getInvitation` and `listUserInvitations` have no `emailVerified` gate at all.

The bearer token (`invitationId`) is by default 32 chars over `[a-zA-Z0-9]` (~190 bits), so the realistic attack vector is leakage of the invitation link rather than brute force.

The fix shape defaults the `emailVerified` gate to on and extends it across all four invitation endpoints (`acceptInvitation`, `rejectInvitation`, `getInvitation`, `listUserInvitations`). This is the same trust-primitive class as GHSA-g38m-r43w-p2q7 (OAuth auto-link); both ship the rule "email equality is not ownership proof; both sides must prove ownership".

### Patches

Fixed in `better-auth@1.6.11`. All four invitation recipient endpoints (`acceptInvitation`, `rejectInvitation`, `getInvitation`, `listUserInvitations`) now require the session user's `emailVerified` to be `true` in addition to the email-string match. The `requireEmailVerificationOnInvitation` option default flips from `false` to `true`, so applications are secure out of the box.

`getInvitation` and `listUserInvitations` use the new `EMAIL_VERIFICATION_REQUIRED_FOR_INVITATION` error code so the wording matches the operation; `acceptInvitation` and `rejectInvitation` keep the existing `EMAIL_VERIFICATION_REQUIRED_BEFORE_ACCEPTING_OR_REJECTING_INVITATION` code. Server-side calls to `listUserInvitations` that pass `ctx.query.email` without an authenticated session continue to bypass the gate; the gate is specific to session-authenticated recipient calls.

Integrators who intentionally accept invitations on unverified sessions can preserve the legacy permissive behavior with `organization({ requireEmailVerificationOnInvitation: false })`. The option is marked `@deprecated`; the gate at each call site carries a `FIXME` pointing at the next-minor follow-up that drops the option and makes the check unconditional. Operators that take this opt-out should understand the takeover risk before doing so.

### Workarounds

If developers cannot upgrade their applications immediately:

- **Set `organization({ requireEmailVerificationOnInvitation: true })`**. Closes `acceptInvitation` and `rejectInvitation` against unverified sessions. Does not close `getInvitation` or `listUserInvitations`.
- **Set `emailAndPassword.requireEmailVerification: true`** (or remove email/password sign-up entirely). Closes the pre-registration step itself.
- **Layer middleware** on the organization invitation routes that asserts `session.user.emailVerified === true` and rejects otherwise.

### Impact

- **Account takeover via pre-account hijacking on the org invitation surface**: the attacker, holding only an unverified self-issued session and the leaked `invitationId`, joins the organization as a member at the invited role.
- **Organization membership reach**: the attacker reads invitation contents and any organization-scoped data the joined role can see, and acts as a member of the victim organization.

### Credit

Reported by @widavies.

### Resources

- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [CWE-345: Insufficient Verification of Data Authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [CWE-862: Missing Authorization](https://cwe.mitre.org/data/definitions/862.html)
- [CWE-441: Unintended Proxy or Intermediary](https://cwe.mitre.org/data/definitions/441.html)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-fmh4-wcc4-5jm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-53514
- https://github.com/better-auth/better-auth/pull/9577
- https://github.com/better-auth/better-auth/commit/23094a628f007f801be6d26e5b15dc5fc6fc4eb8
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
