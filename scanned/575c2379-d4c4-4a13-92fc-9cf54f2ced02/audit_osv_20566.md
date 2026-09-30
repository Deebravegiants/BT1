# [M] CVE-2021-3524

## Summary
Severity: Medium
Advisory: CVE-2021-3524
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2021-3524
Type: osv

## Details
A flaw was found in the Red Hat Ceph Storage RadosGW (Ceph Object Gateway) in versions before 14.2.21. The vulnerability is related to the injection of HTTP headers via a CORS ExposeHeader tag. The newline character in the ExposeHeader tag in the CORS configuration file generates a header injection in the response when the CORS request is made. In addition, the prior bug fix for CVE-2020-10753 did not account for the use of \r as a header separator, thus a new flaw has been created.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FX5ZHI5L7FOHXOSEV3TYBAL66DMLJ7V5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LPCJN2YDZCBMF4FOJXSTAADKFGEQEO7O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZRUNDH2TJRZRWL3DCH2PQ6KROWTPQ7AJ/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00013.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1951674
