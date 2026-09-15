# [M] JLSEC-2026-1341

## Summary
Severity: Medium
Advisory: JLSEC-2026-1341
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1341
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=7.84.0+0 <7.87.0+0

## Details
curl can be told to parse a `.netrc` file for credentials. If that file endsin a line with 4095 consecutive non-white space letters and no newline, curlwould first read past the end of the stack-based buffer, and if the readworks, write a zero byte beyond its boundary.This will in most cases cause a segfault or similar, but circumstances might also cause different outcomes.If a malicious user can provide a custom netrc file to an application or otherwise affect its contents, this flaw could be used as denial-of-service.

## References
- http://seclists.org/fulldisclosure/2023/Jan/19
- http://seclists.org/fulldisclosure/2023/Jan/19
- http://seclists.org/fulldisclosure/2023/Jan/20
- http://seclists.org/fulldisclosure/2023/Jan/20
- https://hackerone.com/reports/1721098
- https://hackerone.com/reports/1721098
- https://security.gentoo.org/glsa/202212-01
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20230110-0006/
- https://security.netapp.com/advisory/ntap-20230110-0006/
- https://support.apple.com/kb/HT213604
- https://support.apple.com/kb/HT213604
- https://support.apple.com/kb/HT213605
- https://support.apple.com/kb/HT213605
