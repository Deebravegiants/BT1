# [H] CVE-2022-1247

## Summary
Severity: High
Advisory: CVE-2022-1247
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-1247
Type: osv

## Details
An issue found in linux-kernel that leads to a race condition in rose_connect(). The rose driver uses rose_neigh->use to represent how many objects are using the rose_neigh. When a user wants to delete a rose_route via rose_ioctl(), the rose driver calls rose_del_node() and removes neighbours only if their “count” and “use” are zero.

## References
- https://access.redhat.com/security/cve/CVE-2022-1247
- https://bugzilla.redhat.com/show_bug.cgi?id=2066799
