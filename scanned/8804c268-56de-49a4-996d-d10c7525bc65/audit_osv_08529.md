# [M] CVE-2016-4080

## Summary
Severity: Medium
Advisory: CVE-2016-4080
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4080
Type: osv

## Details
epan/dissectors/packet-pktc.c in the PKTC dissector in Wireshark 1.12.x before 1.12.11 and 2.0.x before 2.0.3 misparses timestamp fields, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted packet.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=ad097385c05c370440fb810e67f811398efc0ea0
- http://www.debian.org/security/2016/dsa-3585
- http://www.wireshark.org/security/wnpa-sec-2016-23.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12242
