# [H] CVE-2020-27781

## Summary
Severity: High
Advisory: CVE-2020-27781
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-12-18
Source: https://osv.dev/vulnerability/CVE-2020-27781
Type: osv

## Details
User credentials can be manipulated and stolen by Native CephFS consumers of OpenStack Manila, resulting in potential privilege escalation. An Open Stack Manila user can request access to a share to an arbitrary cephx user, including existing users. The access key is retrieved via the interface drivers. Then, all users of the requesting OpenStack project can view the access key. This enables the attacker to target any resource that the user has access to. This can be done to even "admin" users, compromising the ceph administrator. This flaw affects Ceph versions prior to 14.2.16, 15.x prior to 15.2.8, and 16.x prior to 16.2.0.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZJ7FFROL25FYRL6FMI33VRKOD74LINRP/
- https://security.gentoo.org/glsa/202105-39
- https://bugzilla.redhat.com/show_bug.cgi?id=1900109
