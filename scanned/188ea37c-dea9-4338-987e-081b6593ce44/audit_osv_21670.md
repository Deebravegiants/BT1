# [H] CVE-2021-45098

## Summary
Severity: High
Advisory: CVE-2021-45098
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-45098
Type: osv

## Details
An issue was discovered in Suricata before 6.0.4. It is possible to bypass/evade any HTTP-based signature by faking an RST TCP packet with random TCP options of the md5header from the client side. After the three-way handshake, it's possible to inject an RST ACK with a random TCP md5header option. Then, the client can send an HTTP GET request with a forbidden URL. The server will ignore the RST ACK and send the response HTTP packet for the client's request. These packets will not trigger a Suricata reject action.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00029.html
- https://forum.suricata.io/t/suricata-6-0-4-and-5-0-8-released/1942
- https://github.com/OISF/suricata/releases
- https://github.com/OISF/suricata/commit/50e2b973eeec7172991bf8f544ab06fb782b97df
- https://redmine.openinfosecfoundation.org/issues/4710
