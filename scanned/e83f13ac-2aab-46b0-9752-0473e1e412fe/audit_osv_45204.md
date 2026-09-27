# [H] An integer overflow was addressed with improved input validation

## Summary
Severity: High
Advisory: JLSEC-2025-195
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/JLSEC-2025-195
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <23.12.0+0

## Details
An integer overflow was addressed with improved input validation. This issue is fixed in Security Update 2021-005 Catalina, iOS 14.8 and iPadOS 14.8, macOS Big Sur 11.6, watchOS 7.6.2. Processing a maliciously crafted PDF may lead to arbitrary code execution. Apple is aware of a report that this issue may have been actively exploited.

## References
- http://seclists.org/fulldisclosure/2021/Sep/25
- http://seclists.org/fulldisclosure/2021/Sep/26
- http://seclists.org/fulldisclosure/2021/Sep/27
- http://seclists.org/fulldisclosure/2021/Sep/28
- http://seclists.org/fulldisclosure/2021/Sep/38
- http://seclists.org/fulldisclosure/2021/Sep/39
- http://seclists.org/fulldisclosure/2021/Sep/40
- http://seclists.org/fulldisclosure/2021/Sep/50
- http://www.openwall.com/lists/oss-security/2022/09/02/11
- https://security.gentoo.org/glsa/202209-21
- https://support.apple.com/en-us/HT212804
- https://support.apple.com/en-us/HT212805
- https://support.apple.com/en-us/HT212806
- https://support.apple.com/en-us/HT212807
- https://support.apple.com/kb/HT212824
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-30860
