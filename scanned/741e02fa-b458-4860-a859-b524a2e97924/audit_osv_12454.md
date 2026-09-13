# [H] CVE-2018-12121

## Summary
Severity: High
Advisory: CVE-2018-12121
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-12121
Type: osv

## Details
Node.js: All versions prior to Node.js 6.15.0, 8.14.0, 10.14.0 and 11.3.0: Denial of Service with large HTTP headers: By using a combination of many requests with maximum sized headers (almost 80 KB per connection), and carefully timed completion of the headers, it is possible to cause the HTTP server to abort from heap allocation failure. Attack potential is mitigated by the use of a load balancer or other proxy layer.

## References
- http://www.securityfocus.com/bid/106043
- https://access.redhat.com/errata/RHSA-2019:1821
- https://access.redhat.com/errata/RHSA-2019:2258
- https://access.redhat.com/errata/RHSA-2019:3497
- https://security.gentoo.org/glsa/202003-48
- https://security.netapp.com/advisory/ntap-20241227-0008/
- https://nodejs.org/en/blog/vulnerability/november-2018-security-releases/
