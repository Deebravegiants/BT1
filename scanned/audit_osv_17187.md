# [M] CVE-2020-13529

## Summary
Severity: Medium
Advisory: CVE-2020-13529
CVSS: 6.1 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-05-10
Source: https://osv.dev/vulnerability/CVE-2020-13529
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in Systemd 245. A specially crafted DHCP FORCERENEW packet can cause a server running the DHCP client to be vulnerable to a DHCP ACK spoofing attack. An attacker can forge a pair of FORCERENEW and DCHP ACK packets to reconfigure the server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/42TMJVNYRY65B4QCJICBYOEIVZV3KUYI/
- http://www.openwall.com/lists/oss-security/2021/08/04/2
- http://www.openwall.com/lists/oss-security/2021/08/17/3
- http://www.openwall.com/lists/oss-security/2021/09/07/3
- https://security.gentoo.org/glsa/202107-48
- https://security.netapp.com/advisory/ntap-20210625-0005/
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1142
