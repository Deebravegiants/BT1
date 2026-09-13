# [C] When sending data to an MQTT server, libcurl <= 7.73.0 and 7.78.0 could in some circumstances...

## Summary
Severity: Critical
Advisory: JLSEC-2025-29
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-29
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=7.70.0+0 <7.81.0+0

## Details
When sending data to an MQTT server, libcurl <= 7.73.0 and 7.78.0 could in some circumstances erroneously keep a pointer to an already freed memory area and both use that again in a subsequent call to send data and also free it *again*.

## References
- http://seclists.org/fulldisclosure/2022/Mar/29
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1269242
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/APOAK4X73EJTAPTSVT7IRVDMUWVXNWGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RWLEC6YVEM2HWUBX67SDGPSY4CQB72OE/
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20211029-0003/
- https://support.apple.com/kb/HT213183
- https://www.debian.org/security/2022/dsa-5197
- https://www.oracle.com/security-alerts/cpuoct2021.html
