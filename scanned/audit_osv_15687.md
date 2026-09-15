# [C] CVE-2019-18792

## Summary
Severity: Critical
Advisory: CVE-2019-18792
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-01-06
Source: https://osv.dev/vulnerability/CVE-2019-18792
Type: osv

## Details
An issue was discovered in Suricata 5.0.0. It is possible to bypass/evade any tcp based signature by overlapping a TCP segment with a fake FIN packet. The fake FIN packet is injected just before the PUSH ACK packet we want to bypass. The PUSH ACK packet (containing the data) will be ignored by Suricata because it overlaps the FIN packet (the sequence and ack number are identical in the two packets). The client will ignore the fake FIN packet because the ACK flag is not set. Both linux and windows clients are ignoring the injected packet.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00032.html
- https://github.com/OISF/suricata/commit/1c63d3905852f746ccde7e2585600b2199cefb4b
- https://github.com/OISF/suricata/commit/fa692df37a796c3330c81988d15ef1a219afc006
- https://redmine.openinfosecfoundation.org/issues/3324
- https://redmine.openinfosecfoundation.org/issues/3394
