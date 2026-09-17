# [M] JLSEC-2026-1340

## Summary
Severity: Medium
Advisory: JLSEC-2026-1340
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1340
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.81.0+0

## Details
When curl >= 7.20.0 and <= 7.78.0 connects to an IMAP or POP3 server to retrieve data using STARTTLS to upgrade to TLS security, the server can respond and send back multiple responses at once that curl caches. curl would then upgrade to TLS but not flush the in-queue of cached responses but instead continue using and trustingthe responses it got *before* the TLS handshake as if they were authenticated.Using this flaw, it allows a Man-In-The-Middle attacker to first inject the fake responses, then pass-through the TLS traffic from the legitimate server and trick curl into sending data back to the user thinking the attacker's injected data comes from the TLS-protected server.

## References
- http://seclists.org/fulldisclosure/2022/Mar/29
- http://seclists.org/fulldisclosure/2022/Mar/29
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1334763
- https://hackerone.com/reports/1334763
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
- https://support.apple.com/kb/HT213183
- https://support.apple.com/kb/HT213183
