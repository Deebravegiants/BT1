# [M] CVE-2020-12826

## Summary
Severity: Medium
Advisory: CVE-2020-12826
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-12826
Type: osv

## Details
A signal access-control issue was discovered in the Linux kernel before 5.6.5, aka CID-7395ea4e65c2. Because exec_id in include/linux/sched.h is only 32 bits, an integer overflow can interfere with a do_notify_parent protection mechanism. A child process can send an arbitrary signal to a parent process in a different security domain. Exploitation limitations include the amount of elapsed time before an integer overflow occurs, and the lack of scenarios where signals to a parent process present a substantial operational threat.

## References
- https://usn.ubuntu.com/4391-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://usn.ubuntu.com/4369-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.5
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4367-1/
- https://www.openwall.com/lists/kernel-hardening/2020/03/25/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1822077
- https://github.com/torvalds/linux/commit/7395ea4e65c2a00d23185a3f63ad315756ba9cef
- https://lists.openwall.net/linux-kernel/2020/03/24/1803
