# [M] curl 7.1.1 to and including 7.75.0 is vulnerable to an "Exposure of Private Personal Information to...

## Summary
Severity: Medium
Advisory: JLSEC-2025-26
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-26
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
curl 7.1.1 to and including 7.75.0 is vulnerable to an "Exposure of Private Personal Information to an Unauthorized Actor" by leaking credentials in the HTTP Referer: header. libcurl does not strip off user credentials from the URL when automatically populating the Referer: HTTP request header field in outgoing HTTP requests, and therefore risks leaking sensitive data to the server that is the target of the second HTTP request.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://curl.se/docs/CVE-2021-22876.html
- https://hackerone.com/reports/1101882
- https://lists.debian.org/debian-lts-announce/2021/05/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2ZC5BMIOKLBQJSFCHEDN2G2C2SH274BP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ITVWPVGLFISU5BJC2BXBRYSDXTXE2YGC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KQUIOYX2KUU6FIUZVB5WWZ6JHSSYSQWJ/
- https://security.gentoo.org/glsa/202105-36
- https://security.netapp.com/advisory/ntap-20210521-0007/
- https://www.oracle.com//security-alerts/cpujul2021.html
