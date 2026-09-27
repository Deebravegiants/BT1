# [M] A logic error was found in the libmount library of util-linux in the function that allows an...

## Summary
Severity: Medium
Advisory: JLSEC-2025-192
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/JLSEC-2025-192
Type: osv

## Affected
- Julia: `Libmount_jll` — affected >=0 <2.39.3+0
- Julia: `Libuuid_jll` — affected >=0 <2.39.3+0
- Julia: `util_linux_jll` — affected >=0 <2.39.3+0

## Details
A logic error was found in the libmount library of util-linux in the function that allows an unprivileged user to unmount a FUSE filesystem. This flaw allows an unprivileged local attacker to unmount FUSE filesystems that belong to certain other users who have a UID that is a prefix of the UID of the attacker in its string form. An attacker may use this flaw to cause a denial of service to applications that use the affected filesystems.

## References
- http://packetstormsecurity.com/files/170176/snap-confine-must_mkdir_and_open_with_perms-Race-Condition.html
- http://seclists.org/fulldisclosure/2022/Dec/4
- http://www.openwall.com/lists/oss-security/2022/11/30/2
- https://bugzilla.redhat.com/show_bug.cgi?id=2024631https://access.redhat.com/security/cve/CVE-2021-3995
- https://github.com/util-linux/util-linux/commit/57202f5713afa2af20ffbb6ab5331481d0396f8d
- https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.37/v2.37.3-ReleaseNotes
- https://security.gentoo.org/glsa/202401-08
- https://security.netapp.com/advisory/ntap-20221209-0002/
- https://www.openwall.com/lists/oss-security/2022/01/24/2
