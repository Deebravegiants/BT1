# [H] CVE-2022-22728

## Summary
Severity: High
Advisory: CVE-2022-22728
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2022-22728
Type: osv

## Details
A flaw in Apache libapreq2 versions 2.16 and earlier could cause a buffer overflow while processing multipart form uploads. A remote attacker could send a request causing a process crash which could lead to a denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BE5MEHGIQUEIISBCVHM43IN2NBDXBFOJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3HZZKVHYYWACPWONPEFRNPIRE3HYLV4T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2PUUS3JL44UUSLJTSXE46HVKZIW7E7PE/
- http://www.openwall.com/lists/oss-security/2022/08/25/3
- http://www.openwall.com/lists/oss-security/2022/12/30/4
- http://www.openwall.com/lists/oss-security/2022/12/31/1
- http://www.openwall.com/lists/oss-security/2022/12/31/5
- http://www.openwall.com/lists/oss-security/2023/01/02/1
- http://www.openwall.com/lists/oss-security/2023/01/02/2
- https://lists.debian.org/debian-lts-announce/2023/01/msg00009.html
- https://security.gentoo.org/glsa/202305-20
- http://www.openwall.com/lists/oss-security/2022/08/26/4
- http://www.openwall.com/lists/oss-security/2022/12/29/1
- http://www.openwall.com/lists/oss-security/2022/08/25/4
- http://www.openwall.com/lists/oss-security/2023/01/03/2
- https://lists.apache.org/thread/2fsjoor96d47vtkpf76x4yo06nccvy1y
