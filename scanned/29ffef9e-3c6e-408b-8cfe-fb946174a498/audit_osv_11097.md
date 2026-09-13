# [H] CVE-2017-6014

## Summary
Severity: High
Advisory: CVE-2017-6014
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2017-6014
Type: osv

## Details
In Wireshark 2.2.4 and earlier, a crafted or malformed STANAG 4607 capture file will cause an infinite loop and memory exhaustion. If the packet size field in a packet header is null, the offset to read from will not advance, causing continuous attempts to read the same zero length packet. This will quickly exhaust all system memory.

## References
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96284
- https://security.gentoo.org/glsa/201706-12
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13416
