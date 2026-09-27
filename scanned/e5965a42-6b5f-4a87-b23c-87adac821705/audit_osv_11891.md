# [C] CVE-2018-1000007

## Summary
Severity: Critical
Advisory: CVE-2018-1000007
Aliases: CURL-CVE-2018-1000007
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2018-1000007
Type: osv

## Details
libcurl 7.1 through 7.57.0 might accidentally leak authentication data to third parties. When asked to send custom headers in its HTTP requests, libcurl will send that set of headers first to the host in the initial URL but also, if asked to follow redirects and a 30X HTTP response code is returned, to the host mentioned in URL in the `Location:` response header value. Sending the same set of headers to subsequent hosts is in particular a problem for applications that pass on custom `Authorization:` headers, as this header often contains privacy sensitive information or data that could allow others to impersonate the libcurl-using client's request.

## References
- http://www.openwall.com/lists/oss-security/2022/04/27/4
- http://www.securitytracker.com/id/1040274
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3157
- https://access.redhat.com/errata/RHSA-2018:3558
- https://access.redhat.com/errata/RHSA-2019:1543
- https://access.redhat.com/errata/RHSA-2020:0544
- https://access.redhat.com/errata/RHSA-2020:0594
- https://lists.debian.org/debian-lts-announce/2018/01/msg00038.html
- https://usn.ubuntu.com/3554-1/
- https://usn.ubuntu.com/3554-2/
- https://www.debian.org/security/2018/dsa-4098
- https://curl.haxx.se/docs/adv_2018-b3bf.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
