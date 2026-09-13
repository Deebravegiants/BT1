# [C] CVE-2020-6061

## Summary
Severity: Critical
Advisory: CVE-2020-6061
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-19
Source: https://osv.dev/vulnerability/CVE-2020-6061
Type: osv

## Details
An exploitable heap out-of-bounds read vulnerability exists in the way CoTURN 4.5.1.1 web server parses POST requests. A specially crafted HTTP POST request can lead to information leaks and other misbehavior. An attacker needs to send an HTTPS request to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HQZZPI34LAS3SFNW6Z2ZJ46RKVGEODNA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OUVZRXW5ZIGWVKOLF3NPXRPP74YX7BUY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XN2NK6FT7AMW5UIZNXDNHKEAYWAUMGSF/
- https://usn.ubuntu.com/4415-1/
- https://www.debian.org/security/2020/dsa-4711
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-0984
