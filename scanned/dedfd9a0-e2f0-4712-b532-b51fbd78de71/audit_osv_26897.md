# [H] CVE-2023-5517

## Summary
Severity: High
Advisory: CVE-2023-5517
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2023-5517
Type: osv

## Details
A flaw in query-handling code can cause `named` to exit prematurely with an assertion failure when:

  - `nxdomain-redirect <domain>;` is configured, and
  - the resolver receives a PTR query for an RFC 1918 address that would normally result in an authoritative NXDOMAIN response.
This issue affects BIND 9 versions 9.12.0 through 9.16.45, 9.18.0 through 9.18.21, 9.19.0 through 9.19.19, 9.16.8-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- http://www.openwall.com/lists/oss-security/2024/02/13/1
- https://kb.isc.org/docs/cve-2023-5517
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVRDSJVZKMCXKKPP6PNR62T7RWZ3YSDZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PNNHZSZPG2E7NBMBNYPGHCFI4V4XRWNQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGS7JN6FZXUSTC2XKQHH27574XOULYYJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZDZFMEKQTZ4L7RY46FCENWFB5MDT263R/
- https://security.netapp.com/advisory/ntap-20240503-0006/
