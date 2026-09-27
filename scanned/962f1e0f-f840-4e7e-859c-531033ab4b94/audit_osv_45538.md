# [H] JLSEC-2026-1286

## Summary
Severity: High
Advisory: JLSEC-2026-1286
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1286
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
The cgi gem before 0.1.0.2, 0.2.x before 0.2.2, and 0.3.x before 0.3.5 for Ruby allows HTTP response splitting. This is relevant to applications that use untrusted user input either to generate an HTTP response or to create a CGI::Cookie object.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DQR7LWED6VAPD5ATYOBZIGJQPCUBRJBX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DQR7LWED6VAPD5ATYOBZIGJQPCUBRJBX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/THVTYHHEOVLQFCFHWURZYO7PVUPBHRZD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/THVTYHHEOVLQFCFHWURZYO7PVUPBHRZD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YACE6ORF2QBXXBK2V2CM36D7TZMEJVAS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YACE6ORF2QBXXBK2V2CM36D7TZMEJVAS/
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20221228-0004/
- https://security.netapp.com/advisory/ntap-20221228-0004/
- https://www.ruby-lang.org/en/news/2022/11/22/http-response-splitting-in-cgi-cve-2021-33621/
- https://www.ruby-lang.org/en/news/2022/11/22/http-response-splitting-in-cgi-cve-2021-33621/
