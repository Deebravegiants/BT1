# [H] CVE-2019-11478

## Summary
Severity: High
Advisory: CVE-2019-11478
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-11478
Type: osv

## Details
Jonathan Looney discovered that the TCP retransmission queue implementation in tcp_fragment in the Linux kernel could be fragmented when handling certain TCP Selective Acknowledgment (SACK) sequences. A remote attacker could use this to cause a denial of service. This has been fixed in stable kernel releases 4.4.182, 4.9.182, 4.14.127, 4.19.52, 5.1.11, and is fixed in commit f070ef2ac66716357066b683fb0baf55f8191a2e.

## References
- http://www.openwall.com/lists/oss-security/2019/06/28/2
- https://seclists.org/bugtraq/2019/Jul/30
- https://www.kb.cert.org/vuls/id/905115
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2020-010.txt
- http://www.openwall.com/lists/oss-security/2019/10/29/3
- http://packetstormsecurity.com/files/154408/Kernel-Live-Patch-Security-Notice-LSN-0055-1.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2019-0007
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- http://www.openwall.com/lists/oss-security/2019/07/06/3
- http://www.openwall.com/lists/oss-security/2019/07/06/4
- https://cert-portal.siemens.com/productcert/pdf/ssa-462066.pdf
- https://www.oracle.com/security-alerts/cpujan2020.html
- http://www.openwall.com/lists/oss-security/2019/10/24/1
- https://kc.mcafee.com/corporate/index?page=content&id=SB10287
- http://www.vmware.com/security/advisories/VMSA-2019-0010.html
- https://access.redhat.com/errata/RHSA-2019:1699
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44193
- https://security.netapp.com/advisory/ntap-20190625-0001/
- https://www.us-cert.gov/ics/advisories/icsa-19-253-03
