# [M] Weak password requirements in Kiwi TCMS

## Summary
Severity: Medium
Advisory: CVE-2023-22451
Aliases: GHSA-496x-2jqf-hp7g
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-02
Source: https://osv.dev/vulnerability/CVE-2023-22451
Type: osv

## Details
Kiwi TCMS is an open source test management system. In version 11.6 and prior, when users register new accounts and/or change passwords, there is no validation in place which would prevent them from picking an easy to guess password. This issue is resolved by providing defaults for the `AUTH_PASSWORD_VALIDATORS` configuration setting. As of version 11.7, the password can’t be too similar to other personal information, must contain at least 10 characters, can’t be a commonly used password, and can’t be entirely numeric. As a workaround, an administrator may reset all passwords in Kiwi TCMS if they think a weak password may have been chosen.

## References
- https://huntr.dev/bounties/32a873c8-f605-4aae-9272-d80985ef2b73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22451.json
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-496x-2jqf-hp7g
- https://nvd.nist.gov/vuln/detail/CVE-2023-22451
- https://github.com/kiwitcms/Kiwi/commit/3759fb68aed36315cdde9fc573b2fe7c11544985
