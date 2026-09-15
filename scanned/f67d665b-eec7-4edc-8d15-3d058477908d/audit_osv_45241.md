# [H] curl 7.41.0 through 7.73.0 is vulnerable to an improper check for certificate revocation due to...

## Summary
Severity: High
Advisory: JLSEC-2025-25
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-25
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
curl 7.41.0 through 7.73.0 is vulnerable to an improper check for certificate revocation due to insufficient verification of the OCSP response.

## References
- http://seclists.org/fulldisclosure/2021/Apr/50
- http://seclists.org/fulldisclosure/2021/Apr/51
- http://seclists.org/fulldisclosure/2021/Apr/54
- https://cert-portal.siemens.com/productcert/pdf/ssa-200951.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://curl.se/docs/CVE-2020-8286.html
- https://hackerone.com/reports/1048457
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
