# [H] CVE-2018-8022

## Summary
Severity: High
Advisory: CVE-2018-8022
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-8022
Type: osv

## Details
A carefully crafted invalid TLS handshake can cause Apache Traffic Server (ATS) to segfault. This affects version 6.2.2. To resolve this issue users running 6.2.2 should upgrade to 6.2.3 or later versions.

## References
- https://lists.apache.org/thread.html/ce404d2fe16cc59085ece5a6236ccd1549def471a2a9508198d966b1%40%3Cusers.trafficserver.apache.org%3E
- http://www.securityfocus.com/bid/105183
- https://github.com/apache/trafficserver/pull/2147
