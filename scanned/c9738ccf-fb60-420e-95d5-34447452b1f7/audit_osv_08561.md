# [M] CVE-2016-4419

## Summary
Severity: Medium
Advisory: CVE-2016-4419
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-01
Source: https://osv.dev/vulnerability/CVE-2016-4419
Type: osv

## Details
epan/dissectors/packet-spice.c in the SPICE dissector in Wireshark 2.x before 2.0.2 mishandles capability data, which allows remote attackers to cause a denial of service (large loop) via a crafted packet.

## References
- https://www.wireshark.org/security/wnpa-sec-2016-16.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12151
