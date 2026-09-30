# [M] CVE-2016-7176

## Summary
Severity: Medium
Advisory: CVE-2016-7176
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-09
Source: https://osv.dev/vulnerability/CVE-2016-7176
Type: osv

## Details
epan/dissectors/packet-h225.c in the H.225 dissector in Wireshark 2.x before 2.0.6 calls snprintf with one of its input buffers as the output buffer, which allows remote attackers to cause a denial of service (copy overlap and application crash) via a crafted packet.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6d8261994bb928b7e80e3a2478a3d939ea1ef373
- http://www.debian.org/security/2016/dsa-3671
- http://www.securitytracker.com/id/1036760
- https://www.wireshark.org/security/wnpa-sec-2016-51.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12700
- https://code.wireshark.org/review/16852
