# [H] CVE-2019-18625

## Summary
Severity: High
Advisory: CVE-2019-18625
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-06
Source: https://osv.dev/vulnerability/CVE-2019-18625
Type: osv

## Details
An issue was discovered in Suricata 5.0.0. It was possible to bypass/evade any tcp based signature by faking a closed TCP session using an evil server. After the TCP SYN packet, it is possible to inject a RST ACK and a FIN ACK packet with a bad TCP Timestamp option. The client will ignore the RST ACK and the FIN ACK packets because of the bad TCP Timestamp option. Both linux and windows client are ignoring the injected packets.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00032.html
- https://redmine.openinfosecfoundation.org/issues/3286
- https://redmine.openinfosecfoundation.org/issues/3395
- https://github.com/OISF/suricata/commit/9f0294fadca3dcc18c919424242a41e01f3e8318
- https://github.com/OISF/suricata/commit/ea0659de7640cf6a51de5bbd1dbbb0414e4623a0
