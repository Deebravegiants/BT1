# [H] When curl retrieves an HTTP response, it stores the incoming headers so that they can be accessed...

## Summary
Severity: High
Advisory: JLSEC-2026-1342
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1342
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=7.84.0+0 <8.4.0+0

## Details
When curl retrieves an HTTP response, it stores the incoming headers so that
they can be accessed later via the libcurl headers API.

However, curl did not have a limit in how many or how large headers it would
accept in a response, allowing a malicious server to stream an endless series
of headers and eventually cause curl to run out of heap memory.

## References
- http://seclists.org/fulldisclosure/2023/Oct/17
- http://seclists.org/fulldisclosure/2024/Jan/34
- http://seclists.org/fulldisclosure/2024/Jan/37
- http://seclists.org/fulldisclosure/2024/Jan/38
- https://github.com/advisories/GHSA-99j9-jf36-9747
- https://hackerone.com/reports/2072338
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5DCZMYODALBLVOXVJEN2LF2MLANEYL4F
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5DCZMYODALBLVOXVJEN2LF2MLANEYL4F/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/M6KGKB2JNZVT276JYSKI6FV2VFJUGDOJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/M6KGKB2JNZVT276JYSKI6FV2VFJUGDOJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TEAWTYHC3RT6ZRS5OZRHLAIENVN6CCIS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TEAWTYHC3RT6ZRS5OZRHLAIENVN6CCIS/
- https://nvd.nist.gov/vuln/detail/CVE-2023-38039
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20231013-0005
- https://security.netapp.com/advisory/ntap-20231013-0005/
- https://support.apple.com/kb/HT214036
- https://support.apple.com/kb/HT214057
- https://support.apple.com/kb/HT214058
- https://support.apple.com/kb/HT214063
