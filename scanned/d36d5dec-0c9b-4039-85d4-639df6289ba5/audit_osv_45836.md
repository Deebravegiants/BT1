# [H] JLSEC-2026-390

## Summary
Severity: High
Advisory: JLSEC-2026-390
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-390
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.83.1+0

## Details
libcurl provides the `CURLOPT_CERTINFO` option to allow applications torequest details to be returned about a server's certificate chain.Due to an erroneous function, a malicious server could make libcurl built withNSS get stuck in a never-ending busy-loop when trying to retrieve thatinformation.

## References
- https://hackerone.com/reports/1555441
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0009/
- https://www.debian.org/security/2022/dsa-5197
