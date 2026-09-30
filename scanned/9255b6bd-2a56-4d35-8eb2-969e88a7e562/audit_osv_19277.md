# [H] CVE-2020-9494

## Summary
Severity: High
Advisory: CVE-2020-9494
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CVE-2020-9494
Type: osv

## Details
Apache Traffic Server 6.0.0 to 6.2.3, 7.0.0 to 7.1.10, and 8.0.0 to 8.0.7 is vulnerable to certain types of HTTP/2 HEADERS frames that can cause the server to allocate a large amount of memory and spin the thread.

## References
- http://www.openwall.com/lists/oss-security/2021/03/01/2
- https://lists.apache.org/thread.html/rf7f86917f42fdaf904d99560cba0c016e03baea6244c47efeb60ecbe%40%3Cdev.trafficserver.apache.org%3E
- https://www.debian.org/security/2020/dsa-4710
