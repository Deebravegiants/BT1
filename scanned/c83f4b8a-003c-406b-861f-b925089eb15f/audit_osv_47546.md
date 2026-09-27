# [H] CVE-2016-7800

## Summary
Severity: High
Advisory: CVE-2016-7800
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-7800
Type: osv

## Details
Integer underflow in the parse8BIM function in coders/meta.c in GraphicsMagick 1.3.25 and earlier allows remote attackers to cause a denial of service (application crash) via a crafted 8BIM chunk, which triggers a heap-based buffer overflow.

## References
- http://www.securityfocus.com/bid/96135
- https://sourceforge.net/p/graphicsmagick/code/ci/5c7b6d6094a25e99c57f8b18343914ebfd8213ef/
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00094.html
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00097.html
- http://www.debian.org/security/2016/dsa-3746
- http://www.openwall.com/lists/oss-security/2016/10/01/7
- http://www.securityfocus.com/bid/93262
- https://bugzilla.redhat.com/show_bug.cgi?id=1381148
