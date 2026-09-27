# [H] JLSEC-2026-407

## Summary
Severity: High
Advisory: JLSEC-2026-407
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-407
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.2.1+0

## Details
A use after free vulnerability exists in curl <v8.1.0 in the way libcurl offers a feature to verify an SSH server's public key using a SHA 256 hash. When this check fails, libcurl would free the memory for the fingerprint before it returns an error message containing the (now freed) hash. This flaw risks inserting sensitive heap-based data into the error message that might be shown to users or otherwise get leaked and revealed.

## References
- http://seclists.org/fulldisclosure/2023/Jul/47
- http://seclists.org/fulldisclosure/2023/Jul/48
- http://seclists.org/fulldisclosure/2023/Jul/52
- https://hackerone.com/reports/1913733
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230609-0009/
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845
