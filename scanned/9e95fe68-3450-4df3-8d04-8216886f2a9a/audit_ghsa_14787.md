# [M] PocketBase performs password auth and OAuth2 unverified email linking

## Summary
Severity: Medium
Advisory: GHSA-m93w-4fxv-r35v
CVE: CVE-2024-38351
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-18
Source: https://github.com/advisories/GHSA-m93w-4fxv-r35v
Type: github-advisory

## Affected
- Go: `github.com/pocketbase/pocketbase` — affected >=0 <0.22.14

## Details
**In order to be exploited you must have both OAuth2 and Password auth methods enabled.**

A possible attack scenario could be:
- a malicious actor register with the targeted user's email (it is unverified)
- at some later point in time the targeted user stumble on your app and decides to sign-up with OAuth2 (_this step could be also initiated by the attacker by sending an invite email to the targeted user_) 
- on successful OAuth2 auth we search for an existing PocketBase user matching with the OAuth2 user's email and associate them
- because we haven't changed the password of the existing PocketBase user during the linking, the malicious actor has access to the targeted user account and will be able to login with the initially created email/password

To prevent this for happening we now reset the password for this specific case if the previously created user wasn't verified (an exception to this is if the linking is explicit/manual, aka. when you send `Authorization:TOKEN` with the OAuth2 auth call).

Additionally to warn existing users we now send an email alert in case the user has logged in with password but has at least one OAuth2 account linked. It looks something like:

_Hello,
Just to let you know that someone has logged in to your Acme account using a password while you already have OAuth2 GitLab auth linked.
If you have recently signed in with a password, you may disregard this email.
**If you don't recognize the above action, you should immediately change your Acme account password.**
Thanks,
Acme team_

The flow will be further improved with the [ongoing refactoring](https://github.com/pocketbase/pocketbase/discussions/4355) and we will start sending emails for "unrecognized device" logins (OTP and MFA is already implemented and will be available with the next v0.23.0 release in the near future).

## References
- https://github.com/pocketbase/pocketbase/security/advisories/GHSA-m93w-4fxv-r35v
- https://nvd.nist.gov/vuln/detail/CVE-2024-38351
- https://github.com/pocketbase/pocketbase/commit/58ace5d5e7b9b979490019cf8d1b88491e5daec5
- https://github.com/pocketbase/pocketbase
- https://github.com/pocketbase/pocketbase/discussions/4355
