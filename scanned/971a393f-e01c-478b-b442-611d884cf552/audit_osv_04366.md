# [H] Discourse user account takeover via email and invite link

## Summary
Severity: High
Advisory: BIT-discourse-2022-39356
Aliases: CVE-2022-39356, GHSA-x8w7-rwmr-w278
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-39356
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.10

## Details
Discourse is a platform for community discussion. Users who receive an invitation link that is not scoped to a single email address can enter any non-admin user's email and gain access to their account when accepting the invitation. All users should upgrade to the latest version. A workaround is temporarily disabling invitations with `SiteSetting.max_invites_per_day = 0` or scope them to individual email addresses.

## References
- https://github.com/discourse/discourse/pull/18817
- https://github.com/discourse/discourse/security/advisories/GHSA-x8w7-rwmr-w278
- https://nvd.nist.gov/vuln/detail/CVE-2022-39356
