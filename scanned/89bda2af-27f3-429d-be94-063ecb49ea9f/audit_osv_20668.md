# [H] CVE-2021-35970

## Summary
Severity: High
Advisory: CVE-2021-35970
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-30
Source: https://osv.dev/vulnerability/CVE-2021-35970
Type: osv

## Details
Talk 4 in Coral before 4.12.1 allows remote attackers to discover e-mail addresses and other sensitive information via GraphQL because permission checks use an incorrect data type.

## References
- https://github.com/coralproject/talk/compare/v4.12.0...v4.12.1
- https://github.com/coralproject/talk/pull/3599
- https://docs.coralproject.net/coral/api/graphql/#User
- https://github.com/coralproject/talk/issues/3600
