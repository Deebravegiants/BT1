# [H] JLSEC-2026-387

## Summary
Severity: High
Advisory: JLSEC-2026-387
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-387
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.83.1+0

## Details
An information disclosure vulnerability exists in curl 7.65.0 to 7.82.0 are vulnerable that by using an IPv6 address that was in the connection pool but with a different zone id it could reuse a connection instead.

## References
- https://hackerone.com/reports/1546268
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0008/
- https://www.debian.org/security/2022/dsa-5197
