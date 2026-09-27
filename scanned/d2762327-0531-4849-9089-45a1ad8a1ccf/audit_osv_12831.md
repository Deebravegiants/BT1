# [H] CVE-2018-15501

## Summary
Severity: High
Advisory: CVE-2018-15501
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-18
Source: https://osv.dev/vulnerability/CVE-2018-15501
Type: osv

## Details
In ng_pkt in transports/smart_pkt.c in libgit2 before 0.26.6 and 0.27.x before 0.27.4, a remote attacker can send a crafted smart-protocol "ng" packet that lacks a '\0' byte to trigger an out-of-bounds read that leads to DoS.

## References
- https://github.com/libgit2/libgit2/releases/tag/v0.26.6
- https://github.com/libgit2/libgit2/releases/tag/v0.27.4
- https://lists.debian.org/debian-lts-announce/2018/08/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00031.html
- https://www.pro-linux.de/sicherheit/2/44650/denial-of-service-in-libgit2.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=9406
- https://bugzilla.suse.com/show_bug.cgi?id=1104641
- https://github.com/libgit2/libgit2/commit/1f9a8510e1d2f20ed7334eeeddb92c4dd8e7c649
