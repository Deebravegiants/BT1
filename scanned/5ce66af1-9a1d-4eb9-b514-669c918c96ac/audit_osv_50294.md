# [H] CVE-2020-11653

## Summary
Severity: High
Advisory: CVE-2020-11653
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-08
Source: https://osv.dev/vulnerability/CVE-2020-11653
Type: osv

## Details
An issue was discovered in Varnish Cache before 6.0.6 LTS, 6.1.x and 6.2.x before 6.2.3, and 6.3.x before 6.3.2. It occurs when communication with a TLS termination proxy uses PROXY version 2. There can be an assertion failure and daemon restart, which causes a performance loss.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00036.html
- https://varnish-cache.org/security/VSV00005.html#vsv00005
