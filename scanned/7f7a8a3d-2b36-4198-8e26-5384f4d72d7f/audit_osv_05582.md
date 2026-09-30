# [M] BIT-golang-2021-36221

## Summary
Severity: Medium
Advisory: BIT-golang-2021-36221
Aliases: CVE-2021-36221, GO-2021-0245
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-36221
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.7

## Details
Go before 1.15.15 and 1.16.x before 1.16.7 has a race condition that can lead to a net/http/httputil ReverseProxy panic upon an ErrAbortHandler abort.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://groups.google.com/forum/#%21forum/golang-announce
- https://groups.google.com/g/golang-announce/c/JvWG9FUUYT0
- https://groups.google.com/g/golang-announce/c/uHACNfXAZqk
- https://lists.debian.org/debian-lts-announce/2022/01/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00017.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2MU47VKTNXX33ZDLTI2ORRUY3KLJKU6G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HM7U5JNS5WU66Q3S26PFIU2ITB2ATTQ4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J4AMYYHGBYMIWCCR5RCDFI5RAUJOPO5L/
- https://security.gentoo.org/glsa/202208-02
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-36221
