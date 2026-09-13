# [M] JLSEC-2026-1337

## Summary
Severity: Medium
Advisory: JLSEC-2026-1337
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1337
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
curl supports the `-t` command line option, known as `CURLOPT_TELNETOPTIONS`in libcurl. This rarely used option is used to send variable=content pairs toTELNET servers.Due to flaw in the option parser for sending `NEW_ENV` variables, libcurlcould be made to pass on uninitialized data from a stack based buffer to theserver. Therefore potentially revealing sensitive internal information to theserver using a clear-text network protocol.This could happen because curl did not call and use sscanf() correctly whenparsing the string provided by the application.

## References
- http://seclists.org/fulldisclosure/2021/Sep/39
- http://seclists.org/fulldisclosure/2021/Sep/39
- http://seclists.org/fulldisclosure/2021/Sep/40
- http://seclists.org/fulldisclosure/2021/Sep/40
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://hackerone.com/reports/1223882
- https://hackerone.com/reports/1223882
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRUCW2UVNYUDZF72DQLFQR4PJEC6CF7V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRUCW2UVNYUDZF72DQLFQR4PJEC6CF7V/
- https://security.gentoo.org/glsa/202212-01
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20210902-0003/
- https://security.netapp.com/advisory/ntap-20210902-0003/
- https://support.apple.com/kb/HT212804
- https://support.apple.com/kb/HT212804
- https://support.apple.com/kb/HT212805
- https://support.apple.com/kb/HT212805
