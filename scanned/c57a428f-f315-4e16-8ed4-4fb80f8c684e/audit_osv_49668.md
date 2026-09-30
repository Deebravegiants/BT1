# [M] CVE-2019-15292

## Summary
Severity: Medium
Advisory: CVE-2019-15292
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-21
Source: https://osv.dev/vulnerability/CVE-2019-15292
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.9. There is a use-after-free in atalk_proc_exit, related to net/appletalk/atalk_proc.c, net/appletalk/ddp.c, and net/appletalk/sysctl_net_atalk.c.

## References
- https://support.f5.com/csp/article/K27112954?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://support.f5.com/csp/article/K27112954
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6377f787aeb945cae7abbb6474798de129e1f3ac
