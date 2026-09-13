# [M] CVE-2024-31079

## Summary
Severity: Medium
Advisory: CVE-2024-31079
Aliases: BIT-nginx-2024-31079, BIT-nginx-gateway-2024-31079
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-31079
Type: osv

## Details
When NGINX Plus or NGINX OSS are configured to use the HTTP/3 QUIC module, undisclosed HTTP/3 requests can cause NGINX worker processes to terminate or cause other potential impact. This attack requires that a request be specifically timed during the connection draining process, which the attacker has no visibility and limited influence over.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MLAOKJWDALQZBIV3WKGPJ6T5Z56D3PRD/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R7RPLWC35WHEUFCGKNFG62ESNID25TEZ/
- https://my.f5.com/manage/s/article/K000139611
- http://www.openwall.com/lists/oss-security/2024/05/30/4
