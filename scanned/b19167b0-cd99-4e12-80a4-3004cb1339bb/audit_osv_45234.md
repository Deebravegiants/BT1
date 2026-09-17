# [H] curl 7.21.0 to and including 7.73.0 is vulnerable to uncontrolled recursion due to a stack overflow...

## Summary
Severity: High
Advisory: JLSEC-2025-24
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-24
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
curl 7.21.0 to and including 7.73.0 is vulnerable to uncontrolled recursion due to a stack overflow issue in FTP wildcard match parsing.

## References
- http://seclists.org/fulldisclosure/2021/Apr/51
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://curl.se/docs/CVE-2020-8285.html
- https://github.com/curl/curl/issues/6255
- https://hackerone.com/reports/1045844
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00029.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DAEHE2S2QLO4AO4MEEYL75NB7SAH5PSL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NZUVSQHN2ESHMJXNQ2Z7T2EELBB5HJXG/
- https://security.gentoo.org/glsa/202012-14
- https://security.netapp.com/advisory/ntap-20210122-0007/
- https://support.apple.com/kb/HT212325
- https://support.apple.com/kb/HT212326
- https://support.apple.com/kb/HT212327
- https://www.debian.org/security/2021/dsa-4881
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
