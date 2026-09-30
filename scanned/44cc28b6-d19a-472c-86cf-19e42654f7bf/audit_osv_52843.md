# [H] CVE-2022-1729

## Summary
Severity: High
Advisory: CVE-2022-1729
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-1729
Type: osv

## Details
A race condition was found the Linux kernel in perf_event_open() which can be exploited by an unprivileged user to gain root privileges. The bug allows to build several exploit primitives such as kernel address information leak, arbitrary execution, etc.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3ac6487e584a1eb54071dbe1212e05b884136704
- https://security.netapp.com/advisory/ntap-20230214-0006/
- https://www.openwall.com/lists/oss-security/2022/05/20/2
