# [H] CVE-2019-20637

## Summary
Severity: High
Advisory: CVE-2019-20637
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-08
Source: https://osv.dev/vulnerability/CVE-2019-20637
Type: osv

## Details
An issue was discovered in Varnish Cache before 6.0.5 LTS, 6.1.x and 6.2.x before 6.2.2, and 6.3.x before 6.3.1. It does not clear a pointer between the handling of one client request and the next request within the same connection. This sometimes causes information to be disclosed from the connection workspace, such as data structures associated with previous requests within this connection or VCL-related temporary headers.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00031.html
- http://varnish-cache.org/security/VSV00004.html#vsv00004
