# [C] CVE-2020-26154

## Summary
Severity: Critical
Advisory: CVE-2020-26154
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-26154
Type: osv

## Details
url.cpp in libproxy through 0.4.15 is prone to a buffer overflow when PAC is enabled, as demonstrated by a large PAC file that is delivered without a Content-length header.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BID3HVHAF6DA3YJOFDBSAZSMR3ODNIW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WZVZXTFMFTSML3J6OOCDBDYH474BRJSW/
- https://github.com/libproxy/libproxy/pull/126
- https://lists.debian.org/debian-lts-announce/2020/11/msg00024.html
- https://www.debian.org/security/2020/dsa-4800
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00033.html
- https://bugs.debian.org/968366
