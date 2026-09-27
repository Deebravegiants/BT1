# [H] JLSEC-2026-1339

## Summary
Severity: High
Advisory: JLSEC-2026-1339
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1339
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
A user can tell curl >= 7.20.0 and <= 7.78.0 to require a successful upgrade to TLS when speaking to an IMAP, POP3 or FTP server (`--ssl-reqd` on the command line or`CURLOPT_USE_SSL` set to `CURLUSESSL_CONTROL` or `CURLUSESSL_ALL` withlibcurl). This requirement could be bypassed if the server would return a properly crafted but perfectly legitimate response.This flaw would then make curl silently continue its operations **withoutTLS** contrary to the instructions and expectations, exposing possibly sensitive data in clear text over the network.

## References
- http://seclists.org/fulldisclosure/2022/Mar/29
- http://seclists.org/fulldisclosure/2022/Mar/29
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1334111
- https://hackerone.com/reports/1334111
- https://lists.debian.org/debian-lts-announce/2021/09/msg00022.html
- https://lists.debian.org/debian-lts-announce/2021/09/msg00022.html
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/APOAK4X73EJTAPTSVT7IRVDMUWVXNWGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/APOAK4X73EJTAPTSVT7IRVDMUWVXNWGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RWLEC6YVEM2HWUBX67SDGPSY4CQB72OE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RWLEC6YVEM2HWUBX67SDGPSY4CQB72OE/
- https://security.gentoo.org/glsa/202212-01
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20211029-0003/
- https://security.netapp.com/advisory/ntap-20211029-0003/
- https://security.netapp.com/advisory/ntap-20220121-0008/
- https://security.netapp.com/advisory/ntap-20220121-0008/
