# [H] CVE-2021-23240

## Summary
Severity: High
Advisory: CVE-2021-23240
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/CVE-2021-23240
Type: osv

## Details
selinux_edit_copy_tfiles in sudoedit in Sudo before 1.9.5 allows a local unprivileged user to gain file ownership and escalate privileges by replacing a temporary file with a symlink to an arbitrary file target. This affects SELinux RBAC support in permissive mode. Machines without SELinux are not vulnerable.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EE42Y35SMJOLONAIBNYNFC7J44UUZ2Y6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GMY4VSSBIND7VAYSN6T7XIWJRWG4GBB3/
- https://security.gentoo.org/glsa/202101-33
- https://security.netapp.com/advisory/ntap-20210129-0010/
- https://www.sudo.ws/stable.html#1.9.5
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2021-23240
