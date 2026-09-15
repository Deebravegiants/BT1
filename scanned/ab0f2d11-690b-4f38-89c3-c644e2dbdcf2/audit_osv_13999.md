# [M] CVE-2018-6332

## Summary
Severity: Medium
Advisory: CVE-2018-6332
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-6332
Type: osv

## Details
A potential denial-of-service issue in the Proxygen handling of invalid HTTP2 settings which can cause the server to spend disproportionate resources. This affects all supported versions of HHVM (3.24.3 and 3.21.7 and below) when using the proxygen server to handle HTTP2 requests.

## References
- https://hhvm.com/blog/2018/03/15/hhvm-3.25.html
