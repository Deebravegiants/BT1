# [H] CVE-2021-21900

## Summary
Severity: High
Advisory: CVE-2021-21900
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-19
Source: https://osv.dev/vulnerability/CVE-2021-21900
Type: osv

## Details
A code execution vulnerability exists in the dxfRW::processLType() functionality of LibreCad libdxfrw 2.2.0-rc2-19-ge02f3580. A specially-crafted .dxf file can lead to a use-after-free vulnerability. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZTIAMP7QJDKV4ADDLR4GVVX2TXYLHVOZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RDI3HCTCACMIC7I4ILB3NRU6DCMADI5H/
- https://security.gentoo.org/glsa/202305-26
- https://www.debian.org/security/2022/dsa-5077
- https://lists.debian.org/debian-lts-announce/2021/12/msg00002.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1351
