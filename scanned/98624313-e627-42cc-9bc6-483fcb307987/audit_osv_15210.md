# [H] CVE-2019-14494

## Summary
Severity: High
Advisory: CVE-2019-14494
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-01
Source: https://osv.dev/vulnerability/CVE-2019-14494
Type: osv

## Details
An issue was discovered in Poppler through 0.78.0. There is a divide-by-zero error in the function SplashOutputDev::tilingPatternFill at SplashOutputDev.cc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AHYAM32PALHQXL3O4DKIJ3EJB6AKBOVC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DLAQBLBIIL3A5XZQYR4MG3Z4LIPIC42P/
- https://lists.debian.org/debian-lts-announce/2020/11/msg00014.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
- https://usn.ubuntu.com/4091-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/802
- https://gitlab.freedesktop.org/poppler/poppler/merge_requests/317
