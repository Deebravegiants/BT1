# [M] CVE-2020-10194

## Summary
Severity: Medium
Advisory: CVE-2020-10194
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2020-10194
Type: osv

## Details
cs/service/account/AutoCompleteGal.java in Zimbra zm-mailbox before 8.8.15.p8 allows authenticated users to request any GAL account. This differs from the intended behavior in which the domain of the authenticated user must match the domain of the galsync account in the request.

## References
- https://github.com/Zimbra/zm-mailbox/commit/1df440e0efa624d1772a05fb6d397d9beb4bda1e
- https://github.com/Zimbra/zm-mailbox/compare/8.8.15.p7...8.8.15.p8
- https://github.com/Zimbra/zm-mailbox/pull/1020
