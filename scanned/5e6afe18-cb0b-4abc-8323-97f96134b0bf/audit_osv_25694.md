# [C] CVE-2023-41913

## Summary
Severity: Critical
Advisory: CVE-2023-41913
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-07
Source: https://osv.dev/vulnerability/CVE-2023-41913
Type: osv

## Details
strongSwan before 5.9.12 has a buffer overflow and possible unauthenticated remote code execution via a DH public value that exceeds the internal buffer in charon-tkm's DH proxy. The earliest affected version is 5.3.0. An attack can occur via a crafted IKE_SA_INIT message.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YPJZPYHBCRXUQGGKQE6TYH4J4RIJH6HO/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41913.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPJZPYHBCRXUQGGKQE6TYH4J4RIJH6HO/
- https://nvd.nist.gov/vuln/detail/CVE-2023-41913
- https://security.netapp.com/advisory/ntap-20250117-0003/
- https://github.com/strongswan/strongswan/releases
- https://www.strongswan.org/blog/2023/11/20/strongswan-vulnerability-%28cve-2023-41913%29.html
