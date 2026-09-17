# [H] CVE-2016-8682

## Summary
Severity: High
Advisory: CVE-2016-8682
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8682
Type: osv

## Details
The ReadSCTImage function in coders/sct.c in GraphicsMagick 1.3.25 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted SCT header.

## References
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00094.html
- http://www.debian.org/security/2016/dsa-3746
- http://www.securityfocus.com/bid/93597
- http://hg.code.sf.net/p/graphicsmagick/code/rev/0a0dfa81906d
- http://www.openwall.com/lists/oss-security/2016/10/16/6
- https://blogs.gentoo.org/ago/2016/09/15/graphicsmagick-stack-based-buffer-overflow-in-readsctimage-sct-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1385583
