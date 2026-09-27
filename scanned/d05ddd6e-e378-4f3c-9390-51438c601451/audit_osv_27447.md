# [M] Zulip non-admins can invite new users to streams they would not otherwise be able to add existing users to

## Summary
Severity: Medium
Advisory: CVE-2024-21630
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2024-21630
Type: osv

## Details
Zulip is an open-source team collaboration tool. A vulnerability in version 8.0 is similar to CVE-2023-32677, but applies to multi-use invitations, not single-use invitation links as in the prior CVE. Specifically, it applies when the installation has configured non-admins to be able to invite users and create multi-use invitations, and has also configured only admins to be able to invite users to streams. As in CVE-2023-32677, this does not let users invite new users to arbitrary streams, only to streams that the inviter can already see. Version 8.1 fixes this issue. As a workaround, administrators can limit sending of invitations down to users who also have the permission to add users to streams.

## References
- https://zulip.com/help/configure-who-can-invite-to-streams
- https://zulip.com/help/restrict-account-creation#change-who-can-send-invitations
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21630.json
- https://github.com/zulip/zulip/security/advisories/GHSA-87p9-wprh-7rm6
- https://github.com/zulip/zulip/security/advisories/GHSA-mrvp-96q6-jpvc
- https://nvd.nist.gov/vuln/detail/CVE-2024-21630
- https://github.com/zulip/zulip/commit/0df7bd71f32f3b772e2646c6ab0d60c9b610addf
