# [M] PocketBase vulnerable to account pre-hijacking via OAuth2 unverfied->verified autolinking upgrade

## Summary
Severity: Medium
Advisory: GHSA-pq7p-mc74-g65w
CVE: CVE-2026-44166
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-pq7p-mc74-g65w
Type: github-advisory

## Affected
- Go: `github.com/pocketbase/pocketbase` — affected >=0 <0.22.42
- Go: `github.com/pocketbase/pocketbase` — affected >=0.30.0 <0.37.4

## Details
A pre-hijacking issue was discovered with the OAuth2 autolinking by [Alardiians](https://github.com/Alardiians).

In some situations, if an attacker knows the email address of the victim they can create and link an **unverified** PocketBase user in advance by authenticating with one of the OAuth2 app providers, e.g. "A". When the victim gets invited or decides to sign up to your app on their own with provider "B" _(PocketBase OAuth2 auth requires to be with a different provider because we don't allow multiple OAuth2 accounts from the same provider to be associated to a single PocketBase user)_, the user created previously by the attacker will be autolinked, upgraded to **"verified"** and its old password reset.

The upgrade flow operates within the expectations but the problem is that I forgot to clear the previous OAuth2 link(s) leaving the attacker to still have access to the initially created user.

Or in other words, the vulnerability is similar to the [mixed password + OAuth2 auth pre-hijacking issue](https://github.com/pocketbase/pocketbase/security/advisories/GHSA-m93w-4fxv-r35v) that we had in the past but with a slightly different angle.

So with that in mind, and to avoid introducing breaking changes to the auth flows, a new fix was applied that automatically deletes all such pre-existing OAuth2 links on "unverified" to "verified" upgrades.

**While the vulnerability requires some prerequisites, it is considered severe and it is strongly recommended to upgrade to v0.37.4 _(or to v0.22.42 if you are using an older <v0.23.0 release)_.**

## References
- https://github.com/pocketbase/pocketbase/security/advisories/GHSA-pq7p-mc74-g65w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44166
- https://github.com/pocketbase/pocketbase
