# [M] CVE-2021-46141

## Summary
Severity: Medium
Advisory: CVE-2021-46141
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/CVE-2021-46141
Type: osv

## Details
An issue was discovered in uriparser before 0.9.6. It performs invalid free operations in uriFreeUriMembers and uriMakeOwner.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MO6T7WA27H7K3WI2AXUAGPWBGK4HM65D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGIJTDNEMU2V4H3JJBQVKBRHU5GBQKG2/
- https://blog.hartwork.org/posts/uriparser-096-with-security-fixes-released/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00029.html
- https://www.debian.org/security/2022/dsa-5063
- https://github.com/uriparser/uriparser/issues/121
- https://github.com/uriparser/uriparser/pull/124
