# [M] JLSEC-2026-401

## Summary
Severity: Medium
Advisory: JLSEC-2026-401
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-401
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.87.0+0

## Details
A use after free vulnerability exists in curl <7.87.0. Curl can be asked to *tunnel* virtually all protocols it supports through an HTTP proxy. HTTP proxies can (and often do) deny such tunnel operations. When getting denied to tunnel the specific protocols SMB or TELNET, curl would use a heap-allocated struct after it had been freed, in its transfer shutdown code path.

## References
- http://seclists.org/fulldisclosure/2023/Mar/17
- https://hackerone.com/reports/1764858
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230214-0002/
- https://support.apple.com/kb/HT213670
