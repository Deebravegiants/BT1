# [M] JLSEC-2026-386

## Summary
Severity: Medium
Advisory: JLSEC-2026-386
Ecosystem: Julia
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-386
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.83.1+0

## Details
An insufficiently protected credentials vulnerability exists in curl 4.9 to and include curl 7.82.0 are affected that could allow an attacker to extract credentials when follows HTTP(S) redirects is used with authentication could leak credentials to other services that exist on different protocols or port numbers.

## References
- https://hackerone.com/reports/1543773
- https://lists.debian.org/debian-lts-announce/2023/01/msg00028.html
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0008/
- https://www.debian.org/security/2022/dsa-5197
