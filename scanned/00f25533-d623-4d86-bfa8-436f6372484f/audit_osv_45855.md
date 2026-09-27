# [M] JLSEC-2026-408

## Summary
Severity: Medium
Advisory: JLSEC-2026-408
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-408
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.2.1+0

## Details
A denial of service vulnerability exists in curl <v8.1.0 in the way libcurl provides several different backends for resolving host names, selected at build time. If it is built to use the synchronous resolver, it allows name resolves to time-out slow operations using `alarm()` and `siglongjmp()`. When doing this, libcurl used a global buffer that was not mutex protected and a multi-threaded application might therefore crash or otherwise misbehave.

## References
- http://seclists.org/fulldisclosure/2023/Jul/47
- http://seclists.org/fulldisclosure/2023/Jul/48
- http://seclists.org/fulldisclosure/2023/Jul/52
- https://hackerone.com/reports/1929597
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230609-0009/
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845
