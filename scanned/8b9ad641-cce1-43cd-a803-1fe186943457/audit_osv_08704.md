# [M] CVE-2016-5356

## Summary
Severity: Medium
Advisory: CVE-2016-5356
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5356
Type: osv

## Details
wiretap/cosine.c in the CoSine file parser in Wireshark 1.12.x before 1.12.12 and 2.x before 2.0.4 mishandles sscanf unsigned-integer processing, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91140
- http://www.debian.org/security/2016/dsa-3615
- https://www.wireshark.org/security/wnpa-sec-2016-35.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12395
- https://github.com/wireshark/wireshark/commit/a66628e425db725df1ac52a3c573a03357060ddd
- https://github.com/wireshark/wireshark/commit/f5ec0afb766f19519ea9623152cca3bbe2229500
- http://www.openwall.com/lists/oss-security/2016/06/09/3
