# [H] CVE-2017-6347

## Summary
Severity: High
Advisory: CVE-2017-6347
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-6347
Type: osv

## Details
The ip_cmsg_recv_checksum function in net/ipv4/ip_sockglue.c in the Linux kernel before 4.10.1 has incorrect expectations about skb data layout, which allows local users to cause a denial of service (buffer over-read) or possibly have unspecified other impact via crafted system calls, as demonstrated by use of the MSG_MORE flag in conjunction with loopback UDP transmission.

## References
- http://www.securityfocus.com/bid/96487
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ca4ef4574f1ee5252e2cd365f8f5d5bafd048f32
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.1
- http://www.openwall.com/lists/oss-security/2017/02/28/5
- https://bugzilla.redhat.com/show_bug.cgi?id=1427984
- https://github.com/torvalds/linux/commit/ca4ef4574f1ee5252e2cd365f8f5d5bafd048f32
