# [M] CVE-2020-25650

## Summary
Severity: Medium
Advisory: CVE-2020-25650
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-25
Source: https://osv.dev/vulnerability/CVE-2020-25650
Type: osv

## Details
A flaw was found in the way the spice-vdagentd daemon handled file transfers from the host system to the virtual machine. Any unprivileged local guest user with access to the UNIX domain socket path `/run/spice-vdagentd/spice-vdagent-sock` could use this flaw to perform a memory denial of service for spice-vdagentd or even other processes in the VM system. The highest threat from this vulnerability is to system availability. This flaw affects spice-vdagent versions 0.20 and previous versions.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GQT56LATVTB2DJOVVJOKQVMVUXYCT2VB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OIWJ2EIQXWEA2VDBODEATHAT37X4CREP/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1886345
- https://www.openwall.com/lists/oss-security/2020/11/04/1
