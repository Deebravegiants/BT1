# [H] CVE-2014-9914

## Summary
Severity: High
Advisory: CVE-2014-9914
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2014-9914
Type: osv

## Details
Race condition in the ip4_datagram_release_cb function in net/ipv4/datagram.c in the Linux kernel before 3.15.2 allows local users to gain privileges or cause a denial of service (use-after-free) by leveraging incorrect expectations about locking during multithreaded access to internal data structures for IPv4 UDP sockets.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9709674e68646cee5a24e3000b3558d25412203a
- http://source.android.com/security/bulletin/2017-02-01.html
- http://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.2
- http://www.securityfocus.com/bid/96100
- http://www.securitytracker.com/id/1037798
- https://github.com/torvalds/linux/commit/9709674e68646cee5a24e3000b3558d25412203a
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9709674e68646cee5a24e3000b3558d25412203a
- https://github.com/torvalds/linux/commit/9709674e68646cee5a24e3000b3558d25412203a
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9709674e68646cee5a24e3000b3558d25412203a
- https://github.com/torvalds/linux/commit/9709674e68646cee5a24e3000b3558d25412203a
