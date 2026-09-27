# [M] CVE-2016-6510

## Summary
Severity: Medium
Advisory: CVE-2016-6510
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6510
Type: osv

## Details
Off-by-one error in epan/dissectors/packet-rlc.c in the RLC dissector in Wireshark 1.12.x before 1.12.13 and 2.x before 2.0.5 allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=47a5fa850b388fcf4ea762073806f01b459820fe
- http://www.debian.org/security/2016/dsa-3648
- http://www.wireshark.org/security/wnpa-sec-2016-46.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12664
- http://openwall.com/lists/oss-security/2016/07/28/3
