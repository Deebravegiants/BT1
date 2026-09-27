# [M] CVE-2018-16597

## Summary
Severity: Medium
Advisory: CVE-2018-16597
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-16597
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.8. Incorrect access checking in overlayfs mounts could be used by local attackers to modify or truncate files in the underlying filesystem.

## References
- http://packetstormsecurity.com/files/153702/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://seclists.org/bugtraq/2019/Jul/33
- https://support.f5.com/csp/article/K22691834
- http://lists.opensuse.org/opensuse-security-announce/2018-10/msg00033.html
- http://www.securityfocus.com/bid/105394
- https://bugzilla.suse.com/show_bug.cgi?id=1106512
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c0ca3d70e8d3cf81e2255a217f7ca402f5ed0862
- https://security.netapp.com/advisory/ntap-20190204-0001/
