# [M] Invites restricted to an email or invite links restricted to an email domain may be bypassed by a under certain conditions in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-31096
Aliases: CVE-2022-31096, GHSA-rvp8-459h-282r
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-31096
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is an open source discussion platform. Under certain conditions, a logged in user can redeem an invite with an email that either doesn't match the invite's email or does not adhere to the email domain restriction of an invite link. The impact of this flaw is aggravated when the invite has been configured to add the user that accepts the invite into restricted groups. Once a user has been incorrectly added to a restricted group, the user may then be able to view content which that are restricted to the respective group. Users are advised to upgrade to the current stable releases. There are no known workarounds to this issue.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-rvp8-459h-282r
- https://nvd.nist.gov/vuln/detail/CVE-2022-31096
