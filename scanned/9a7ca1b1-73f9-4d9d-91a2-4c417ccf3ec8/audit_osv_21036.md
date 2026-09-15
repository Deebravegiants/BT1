# [M] CVE-2021-3996

## Summary
Severity: Medium
Advisory: CVE-2021-3996
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3996
Type: osv

## Details
A logic error was found in the libmount library of util-linux in the function that allows an unprivileged user to unmount a FUSE filesystem. This flaw allows a local user on a vulnerable system to unmount other users' filesystems that are either world-writable themselves (like /tmp) or mounted in a world-writable directory. An attacker may use this flaw to cause a denial of service to applications that use the affected filesystems.

## References
- http://packetstormsecurity.com/files/170176/snap-confine-must_mkdir_and_open_with_perms-Race-Condition.html
- http://seclists.org/fulldisclosure/2022/Dec/4
- http://www.openwall.com/lists/oss-security/2022/11/30/2
- https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.37/v2.37.3-ReleaseNotes
- https://security.gentoo.org/glsa/202401-08
- https://security.netapp.com/advisory/ntap-20221209-0002/
- https://access.redhat.com/security/cve/CVE-2021-3996
- https://bugzilla.redhat.com/show_bug.cgi?id=2024628
- https://github.com/util-linux/util-linux/commit/166e87368ae88bf31112a30e078cceae637f4cdb
- https://www.openwall.com/lists/oss-security/2022/01/24/2
