# [M] CVE-2016-4416

## Summary
Severity: Medium
Advisory: CVE-2016-4416
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-01
Source: https://osv.dev/vulnerability/CVE-2016-4416
Type: osv

## Details
epan/dissectors/packet-ieee80211.c in the IEEE 802.11 dissector in Wireshark 2.x before 2.0.2 mishandles the Grouping subfield, which allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted packet.

## References
- https://www.wireshark.org/security/wnpa-sec-2016-13.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11818
