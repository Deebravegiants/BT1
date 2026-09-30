# [H] CVE-2019-8956

## Summary
Severity: High
Advisory: CVE-2019-8956
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-01
Source: https://osv.dev/vulnerability/CVE-2019-8956
Type: osv

## Details
In the Linux Kernel before versions 4.20.8 and 4.19.21 a use-after-free error in the "sctp_sendmsg()" function (net/sctp/socket.c) when handling SCTP_SENDALL flag can be exploited to corrupt memory.

## References
- https://secuniaresearch.flexerasoftware.com/secunia_research/2019-5/
- https://support.f5.com/csp/article/K12671141
- https://usn.ubuntu.com/3930-1/
- https://usn.ubuntu.com/3930-2/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.21
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.8
- https://git.kernel.org/cgit/linux/kernel/git/stable/linux-stable.git/commit/?id=ba59fb0273076637f0add4311faa990a5eec27c0
