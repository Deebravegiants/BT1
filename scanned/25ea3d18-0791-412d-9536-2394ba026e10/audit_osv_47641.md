# [H] CVE-2016-9793

## Summary
Severity: High
Advisory: CVE-2016-9793
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9793
Type: osv

## Details
The sock_setsockopt function in net/core/sock.c in the Linux kernel before 4.8.14 mishandles negative values of sk_sndbuf and sk_rcvbuf, which allows local users to cause a denial of service (memory corruption and system crash) or possibly have unspecified other impact by leveraging the CAP_NET_ADMIN capability for a crafted setsockopt system call with the (1) SO_SNDBUFFORCE or (2) SO_RCVBUFFORCE option.

## References
- https://source.android.com/security/bulletin/2017-03-01.html
- http://www.securityfocus.com/bid/94655
- http://www.securitytracker.com/id/1037968
- https://access.redhat.com/errata/RHSA-2017:0931
- https://access.redhat.com/errata/RHSA-2017:0933
- https://github.com/xairy/kernel-exploits/tree/master/CVE-2016-9793
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.14
- https://access.redhat.com/errata/RHSA-2017:0932
- https://bugzilla.redhat.com/show_bug.cgi?id=1402013
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b98b0bc8c431e3ceb4b26b0dfc8db509518fb290
- http://www.openwall.com/lists/oss-security/2016/12/03/1
- https://github.com/torvalds/linux/commit/b98b0bc8c431e3ceb4b26b0dfc8db509518fb290
