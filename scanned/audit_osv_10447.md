# [M] CVE-2017-15705

## Summary
Severity: Medium
Advisory: CVE-2017-15705
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-09-17
Source: https://osv.dev/vulnerability/CVE-2017-15705
Type: osv

## Details
A denial of service vulnerability was identified that exists in Apache SpamAssassin before 3.4.2. The vulnerability arises with certain unclosed tags in emails that cause markup to be handled incorrectly leading to scan timeouts. In Apache SpamAssassin, using HTML::Parser, we setup an object and hook into the begin and end tag event handlers In both cases, the "open" event is immediately followed by a "close" event - even if the tag *does not* close in the HTML being parsed. Because of this, we are missing the "text" event to deal with the object normally. This can cause carefully crafted emails that might take more scan time than expected leading to a Denial of Service. The issue is possibly a bug or design decision in HTML::Parser that specifically impacts the way Apache SpamAssassin uses the module with poorly formed html. The exploit has been seen in the wild but not believed to have been purposefully part of a Denial of Service attempt. We are concerned that there may be attempts to abuse the vulnerability in the future.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00002.html
- https://lists.apache.org/thread.html/7f6a16bc0fd0fd5e67c7fd95bd655069a2ac7d1f88e42d3c853e601c%40%3Cannounce.apache.org%3E
- http://www.securityfocus.com/bid/105347
- https://access.redhat.com/errata/RHSA-2018:2916
- https://lists.debian.org/debian-lts-announce/2018/11/msg00016.html
- https://security.gentoo.org/glsa/201812-07
- https://usn.ubuntu.com/3811-1/
- https://usn.ubuntu.com/3811-2/
