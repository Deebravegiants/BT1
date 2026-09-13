# [M] CVE-2020-26034

## Summary
Severity: Medium
Advisory: CVE-2020-26034
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-26034
Type: osv

## Details
An account-enumeration issue was discovered in Zammad before 3.4.1. The Create User functionality is implemented in a way that would enable an anonymous user to guess valid user email addresses. The application responds differently depending on whether the input supplied was recognized as associated with a valid user.

## References
- https://zammad.com/news/security-advisory-zaa-2020-14
