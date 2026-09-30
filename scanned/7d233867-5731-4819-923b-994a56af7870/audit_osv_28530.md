# [M] CVE-2024-34161

## Summary
Severity: Medium
Advisory: CVE-2024-34161
Aliases: BIT-nginx-2024-34161, BIT-nginx-gateway-2024-34161
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-34161
Type: osv

## Details
When NGINX Plus or NGINX OSS are configured to use the HTTP/3 QUIC module and the network infrastructure supports a Maximum Transmission Unit (MTU) of 4096 or greater without fragmentation, undisclosed QUIC packets can cause NGINX worker processes to leak previously freed memory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MLAOKJWDALQZBIV3WKGPJ6T5Z56D3PRD/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R7RPLWC35WHEUFCGKNFG62ESNID25TEZ/
- https://my.f5.com/manage/s/article/K000139627
- http://www.openwall.com/lists/oss-security/2024/05/30/4
