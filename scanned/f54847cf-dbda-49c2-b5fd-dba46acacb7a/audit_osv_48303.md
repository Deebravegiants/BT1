# [M] CVE-2017-5986

## Summary
Severity: Medium
Advisory: CVE-2017-5986
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-18
Source: https://osv.dev/vulnerability/CVE-2017-5986
Type: osv

## Details
Race condition in the sctp_wait_for_sndbuf function in net/sctp/socket.c in the Linux kernel before 4.9.11 allows local users to cause a denial of service (assertion failure and panic) via a multithreaded application that peels off an association in a certain buffer-full state.

## References
- http://www.securityfocus.com/bid/96222
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.11
- https://access.redhat.com/errata/RHSA-2017:1308
- http://www.debian.org/security/2017/dsa-3804
- https://bugzilla.redhat.com/show_bug.cgi?id=1420276
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2dcab598484185dea7ec22219c76dcdd59e3cb90
- http://www.openwall.com/lists/oss-security/2017/02/14/6
- https://github.com/torvalds/linux/commit/2dcab598484185dea7ec22219c76dcdd59e3cb90
