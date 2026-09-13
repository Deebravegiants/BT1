# [M] JLSEC-2026-1336

## Summary
Severity: Medium
Advisory: JLSEC-2026-1336
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1336
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
When curl is instructed to get content using the metalink feature, and a user name and password are used to download the metalink XML file, those same credentials are then subsequently passed on to each of the servers from which curl will download or try to download the contents from. Often contrary to the user's expectations and intentions and without telling the user it happened.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1213181
- https://hackerone.com/reports/1213181
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRUCW2UVNYUDZF72DQLFQR4PJEC6CF7V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRUCW2UVNYUDZF72DQLFQR4PJEC6CF7V/
- https://security.gentoo.org/glsa/202212-01
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20210902-0003/
- https://security.netapp.com/advisory/ntap-20210902-0003/
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
