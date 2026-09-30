# [H] CVE-2019-11477

## Summary
Severity: High
Advisory: CVE-2019-11477
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-11477
Type: osv

## Details
Jonathan Looney discovered that the TCP_SKB_CB(skb)->tcp_gso_segs value was subject to an integer overflow in the Linux kernel when handling TCP Selective Acknowledgments (SACKs). A remote attacker could use this to cause a denial of service. This has been fixed in stable kernel releases 4.4.182, 4.9.182, 4.14.127, 4.19.52, 5.1.11, and is fixed in commit 3b4929f65b0d8249f19a50245cd88ed1a2f78cff.

## References
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- http://www.openwall.com/lists/oss-security/2019/10/24/1
- https://www.us-cert.gov/ics/advisories/icsa-19-253-03
- http://www.openwall.com/lists/oss-security/2019/07/06/3
- https://access.redhat.com/errata/RHSA-2019:1594
- https://security.netapp.com/advisory/ntap-20190625-0001/
- http://packetstormsecurity.com/files/153346/Kernel-Live-Patch-Security-Notice-LSN-0052-1.html
- https://access.redhat.com/errata/RHSA-2019:1699
- https://kc.mcafee.com/corporate/index?page=content&id=SB10287
- https://support.f5.com/csp/article/K78234183
- http://www.openwall.com/lists/oss-security/2019/06/28/2
- http://www.openwall.com/lists/oss-security/2019/07/06/4
- https://access.redhat.com/security/vulnerabilities/tcpsack
- https://www.synology.com/security/advisory/Synology_SA_19_28
- https://access.redhat.com/errata/RHSA-2019:1602
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44193
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2019-0006
- http://www.openwall.com/lists/oss-security/2019/06/20/3
