# [M] A double free vulnerability exists in libcurl <8.0.0 when sharing HSTS data between separate...

## Summary
Severity: Medium
Advisory: JLSEC-2025-32
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-32
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=7.88.1+0 <8.0.1+0

## Details
A double free vulnerability exists in libcurl <8.0.0 when sharing HSTS data between separate "handles". This sharing was introduced without considerations for do this sharing across separate threads but there was no indication of this fact in the documentation. Due to missing mutexes or thread locks, two threads sharing the same HSTS data could end up doing a double-free or use-after-free.

## References
- https://hackerone.com/reports/1897203
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0010/
