# [H] CVE-2018-25032

## Summary
Severity: High
Advisory: CVE-2018-25032
Aliases: GHSA-jc36-42cf-vqwj, PSF-2022-3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2018-25032
Type: osv

## Details
zlib before 1.2.12 allows memory corruption when deflating (i.e., when compressing) if the input has many distant matches.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-333517.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-419740.html
- https://cert-portal.siemens.com/productcert/html/ssa-470355.html
- https://cert-portal.siemens.com/productcert/html/ssa-565386.html
- https://cert-portal.siemens.com/productcert/html/ssa-942865.html
- http://seclists.org/fulldisclosure/2022/May/33
- http://seclists.org/fulldisclosure/2022/May/35
- http://seclists.org/fulldisclosure/2022/May/38
- http://www.openwall.com/lists/oss-security/2022/03/25/2
- https://cert-portal.siemens.com/productcert/pdf/ssa-333517.pdf
- https://lists.debian.org/debian-lts-announce/2022/04/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/05/msg00008.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DCZFIJBJTZ7CL5QXBFKTQ22Q26VINRUF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DF62MVMH3QUGMBDCB3DY2ERQ6EBHTADB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JZZPTWRYQULAOL3AW7RZJNVZ2UONXCV4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NS2D2GFPFGOJUL4WQ3DUAY7HF4VWQ77F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VOKNP2L734AEL47NRYGVZIKEFOUBQY5Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOKFMSNQ5D5WGMALBNBXU3GE442V74WU/
