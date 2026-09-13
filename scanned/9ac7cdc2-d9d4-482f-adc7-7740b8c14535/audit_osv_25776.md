# [H] CVE-2023-4408

## Summary
Severity: High
Advisory: CVE-2023-4408
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2023-4408
Type: osv

## Details
The DNS message parsing code in `named` includes a section whose computational complexity is overly high. It does not cause problems for typical DNS traffic, but crafted queries and responses may cause excessive CPU load on the affected `named` instance by exploiting this flaw. This issue affects both authoritative servers and recursive resolvers.
This issue affects BIND 9 versions 9.0.0 through 9.16.45, 9.18.0 through 9.18.21, 9.19.0 through 9.19.19, 9.9.3-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- http://www.openwall.com/lists/oss-security/2024/02/13/1
- https://kb.isc.org/docs/cve-2023-4408
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVRDSJVZKMCXKKPP6PNR62T7RWZ3YSDZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PNNHZSZPG2E7NBMBNYPGHCFI4V4XRWNQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGS7JN6FZXUSTC2XKQHH27574XOULYYJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZDZFMEKQTZ4L7RY46FCENWFB5MDT263R/
- https://security.netapp.com/advisory/ntap-20240426-0001/
