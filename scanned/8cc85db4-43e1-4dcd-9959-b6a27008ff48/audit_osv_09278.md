# [M] CVE-2016-9375

## Summary
Severity: Medium
Advisory: CVE-2016-9375
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-17
Source: https://osv.dev/vulnerability/CVE-2016-9375
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.1 and 2.0.0 to 2.0.7, the DTN dissector could go into an infinite loop, triggered by network traffic or a capture file. This was addressed in epan/dissectors/packet-dtn.c by checking whether SDNV evaluation was successful.

## References
- http://www.securitytracker.com/id/1037313
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=be6a10afc59f8182b9884d02f9857d547539fe8a
- http://www.debian.org/security/2016/dsa-3719
- http://www.securityfocus.com/bid/94369
- https://www.wireshark.org/security/wnpa-sec-2016-62.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13097
