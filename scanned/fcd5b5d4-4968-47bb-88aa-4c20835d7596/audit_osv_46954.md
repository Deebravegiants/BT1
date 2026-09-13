# [M] CVE-2015-8504

## Summary
Severity: Medium
Advisory: CVE-2015-8504
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2015-8504
Type: osv

## Details
Qemu, when built with VNC display driver support, allows remote attackers to cause a denial of service (arithmetic exception and application crash) via crafted SetPixelFormat messages from a client.

## References
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/12/08/7
- http://www.securityfocus.com/bid/78708
- https://bugzilla.redhat.com/show_bug.cgi?id=1289541
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2015/12/08/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1289541
- https://bugzilla.redhat.com/show_bug.cgi?id=1289541
- http://git.qemu-project.org/?p=qemu.git%3Ba=commitdiff%3Bh=4c65fed8bdf96780735dbdb92a8
