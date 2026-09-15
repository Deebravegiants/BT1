# [M] Storing unencrypted LDAP passwords in feedbacksystem

## Summary
Severity: Medium
Advisory: CVE-2023-37468
Aliases: GHSA-g28r-8wg3-7349
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-37468
Type: osv

## Details
Feedbacksystem is a personalized feedback system for students using artificial intelligence. Passwords of users using LDAP login are stored in clear text in the database. The LDAP users password is passed unencrypted in the LoginController.scala and stored in the database when logging in for the first time. Users using only local login or the cas login are not affected. This issue has been patched in version 1.19.2.

## References
- https://github.com/thm-mni-ii/feedbacksystem/releases/tag/v1.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37468.json
- https://github.com/thm-mni-ii/feedbacksystem/security/advisories/GHSA-g28r-8wg3-7349
- https://nvd.nist.gov/vuln/detail/CVE-2023-37468
- https://github.com/thm-mni-ii/feedbacksystem/commit/8d896125263e1efb1b70990987c7704426325bcf
