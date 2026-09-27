# [M] CVE-2016-4082

## Summary
Severity: Medium
Advisory: CVE-2016-4082
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4082
Type: osv

## Details
epan/dissectors/packet-gsm_cbch.c in the GSM CBCH dissector in Wireshark 1.12.x before 1.12.11 and 2.0.x before 2.0.3 uses the wrong variable to index an array, which allows remote attackers to cause a denial of service (out-of-bounds access and application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=0fe522dfc689c3ebd119f2a6775d1f275c5f04d8
- http://www.debian.org/security/2016/dsa-3585
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.wireshark.org/security/wnpa-sec-2016-26.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12278
