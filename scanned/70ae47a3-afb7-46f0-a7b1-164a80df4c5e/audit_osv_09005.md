# [M] CVE-2016-7180

## Summary
Severity: Medium
Advisory: CVE-2016-7180
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-09
Source: https://osv.dev/vulnerability/CVE-2016-7180
Type: osv

## Details
epan/dissectors/packet-ipmi-trace.c in the IPMI trace dissector in Wireshark 2.x before 2.0.6 does not properly consider whether a string is constant, which allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted packet.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=5213496250aceff086404c568e3718ebc0060934
- http://www.debian.org/security/2016/dsa-3671
- http://www.securitytracker.com/id/1036760
- https://www.wireshark.org/security/wnpa-sec-2016-55.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12782
- https://code.wireshark.org/review/17289
