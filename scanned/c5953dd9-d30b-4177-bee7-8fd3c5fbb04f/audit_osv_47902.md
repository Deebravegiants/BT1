# [H] CVE-2017-14497

## Summary
Severity: High
Advisory: CVE-2017-14497
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-15
Source: https://osv.dev/vulnerability/CVE-2017-14497
Type: osv

## Details
The tpacket_rcv function in net/packet/af_packet.c in the Linux kernel before 4.13 mishandles vnet headers, which might allow local users to cause a denial of service (buffer overflow, and disk and memory corruption) or possibly have unspecified other impact via crafted system calls.

## References
- http://www.securitytracker.com/id/1040106
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/100871
- http://www.securitytracker.com/id/1039371
- https://source.android.com/security/bulletin/2018-01-01
- http://seclists.org/oss-sec/2017/q3/476
- https://bugzilla.redhat.com/show_bug.cgi?id=1492593
- https://github.com/torvalds/linux/commit/edbd58be15a957f6a760c4a514cd475217eb97fd
- https://marc.info/?l=linux-kernel&m=150394500728906&w=2
- https://marc.info/?t=150394517700001&r=1&w=2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=edbd58be15a957f6a760c4a514cd475217eb97fd
