# [M] CVE-2019-5108

## Summary
Severity: Medium
Advisory: CVE-2019-5108
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-5108
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the Linux kernel prior to mainline 5.3. An attacker could exploit this vulnerability by triggering AP to send IAPP location updates for stations before the required authentication process has completed. This could lead to different denial-of-service scenarios, either by causing CAM table attacks, or by leading to traffic flapping if faking already existing clients in other nearby APs of the same wireless infrastructure. An attacker can forge Authentication and Association Request packets to trigger this vulnerability.

## References
- https://usn.ubuntu.com/4286-2/
- https://usn.ubuntu.com/4287-1/
- http://packetstormsecurity.com/files/156455/Kernel-Live-Patch-Security-Notice-LSN-0063-1.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4285-1/
- https://usn.ubuntu.com/4287-2/
- https://www.debian.org/security/2020/dsa-4698
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://security.netapp.com/advisory/ntap-20200204-0002/
- https://usn.ubuntu.com/4286-1/
- https://git.kernel.org/linus/3e493173b7841259a08c5c8e5cbe90adb349da7e
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0900
