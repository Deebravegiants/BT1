# [M] CVE-2016-7178

## Summary
Severity: Medium
Advisory: CVE-2016-7178
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-09
Source: https://osv.dev/vulnerability/CVE-2016-7178
Type: osv

## Details
epan/dissectors/packet-umts_fp.c in the UMTS FP dissector in Wireshark 2.x before 2.0.6 does not ensure that memory is allocated for certain data structures, which allows remote attackers to cause a denial of service (invalid write access and application crash) via a crafted packet.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=315bba7c645b75af24215c6303d187b188610bba
- http://www.debian.org/security/2016/dsa-3671
- http://www.securitytracker.com/id/1036760
- https://www.wireshark.org/security/wnpa-sec-2016-53.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12751
- https://code.wireshark.org/review/17094
