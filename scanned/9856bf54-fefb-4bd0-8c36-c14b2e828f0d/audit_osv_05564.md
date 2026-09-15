# [M] BIT-golang-2020-15586

## Summary
Severity: Medium
Advisory: BIT-golang-2020-15586
Aliases: CVE-2020-15586, GO-2021-0224
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-15586
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.14.0 <1.14.5

## Details
Go before 1.13.13 and 1.14.x before 1.14.5 has a data race in some net/http servers, as demonstrated by the httputil.ReverseProxy Handler, because it reads a request body and writes a response at the same time.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00082.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00030.html
- https://groups.google.com/forum/#%21topic/golang-announce/XZNfaiwgt2w
- https://groups.google.com/forum/#%21topic/golang-announce/f2c5bqrGH_g
- https://lists.debian.org/debian-lts-announce/2020/11/msg00037.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00038.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OCR6LAKCVKL55KJQPPBBWVQGOP7RL2RW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WIRVUHD7TJIT7JJ33FKHIVTHPYABYPHR/
- https://security.netapp.com/advisory/ntap-20200731-0005/
- https://www.cloudfoundry.org/blog/cve-2020-15586/
- https://www.debian.org/security/2021/dsa-4848
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-15586
