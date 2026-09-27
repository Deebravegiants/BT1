# [M] JLSEC-2026-388

## Summary
Severity: Medium
Advisory: JLSEC-2026-388
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-388
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.83.1+0

## Details
A insufficiently protected credentials vulnerability in fixed in curl 7.83.0 might leak authentication or cookie header data on HTTP redirects to the same host but another port number.

## References
- https://hackerone.com/reports/1547048
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7N5ZBWLNNPZKFK7Q4KEHGCJ2YELQEUJP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKKOQXPYLMBSEVDHFS32BPBR3ZQJKY5B/
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0008/
- https://www.debian.org/security/2022/dsa-5197
