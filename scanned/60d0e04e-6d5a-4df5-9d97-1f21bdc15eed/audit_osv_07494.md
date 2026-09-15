# [M] BIT-sqlite-2020-15358

## Summary
Severity: Medium
Advisory: BIT-sqlite-2020-15358
Aliases: A-192605364, ASB-A-192605364, CVE-2020-15358
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-15358
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.32.3

## Details
In SQLite before 3.32.3, select.c mishandles query-flattener optimization, leading to a multiSelectOrderBy heap overflow because of misuse of transitive properties for constant propagation.

## References
- http://seclists.org/fulldisclosure/2020/Dec/32
- http://seclists.org/fulldisclosure/2020/Nov/19
- http://seclists.org/fulldisclosure/2020/Nov/20
- http://seclists.org/fulldisclosure/2020/Nov/22
- http://seclists.org/fulldisclosure/2021/Feb/14
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://security.gentoo.org/glsa/202007-26
- https://security.netapp.com/advisory/ntap-20200709-0001/
- https://support.apple.com/kb/HT211843
- https://support.apple.com/kb/HT211844
- https://support.apple.com/kb/HT211847
- https://support.apple.com/kb/HT211850
- https://support.apple.com/kb/HT211931
- https://support.apple.com/kb/HT212147
- https://usn.ubuntu.com/4438-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.sqlite.org/src/info/10fa79d00f8091e5
