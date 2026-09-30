# [M] CVE-2019-14851

## Summary
Severity: Medium
Advisory: CVE-2019-14851
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2019-14851
Type: osv

## Details
A denial of service vulnerability was discovered in nbdkit. A client issuing a certain sequence of commands could possibly trigger an assertion failure, causing nbdkit to exit. This issue only affected nbdkit versions 1.12.7, 1.14.1, and 1.15.1.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1757259
- https://www.redhat.com/archives/libguestfs/2019-September/msg00272.html
