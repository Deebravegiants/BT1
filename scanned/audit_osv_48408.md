# [H] CVE-2017-7482

## Summary
Severity: High
Advisory: CVE-2017-7482
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-30
Source: https://osv.dev/vulnerability/CVE-2017-7482
Type: osv

## Details
In the Linux kernel before version 4.12, Kerberos 5 tickets decoded when using the RXRPC keys incorrectly assumes the size of a field. This could lead to the size-remaining variable wrapping and the data pointer going over the end of the buffer. This could possibly lead to memory corruption and possible privilege escalation.

## References
- http://www.securitytracker.com/id/1038787
- https://access.redhat.com/errata/RHSA-2019:0641
- https://www.debian.org/security/2017/dsa-3927
- https://www.debian.org/security/2017/dsa-3945
- http://www.securityfocus.com/bid/99299
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7482
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5f2f97656ada8d811d3c1bef503ced266fcd53a0
- http://seclists.org/oss-sec/2017/q2/602
