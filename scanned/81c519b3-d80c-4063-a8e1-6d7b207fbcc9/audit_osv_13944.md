# [H] CVE-2018-5733

## Summary
Severity: High
Advisory: CVE-2018-5733
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5733
Type: osv

## Details
A malicious client which is allowed to send very large amounts of traffic (billions of packets) to a DHCP server can eventually overflow a 32-bit reference counter, potentially causing dhcpd to crash. Affects ISC DHCP 4.1.0 -> 4.1-ESV-R15, 4.2.0 -> 4.2.8, 4.3.0 -> 4.3.6, 4.4.0.

## References
- http://www.securityfocus.com/bid/103188
- http://www.securitytracker.com/id/1040437
- https://access.redhat.com/errata/RHSA-2018:0469
- https://access.redhat.com/errata/RHSA-2018:0483
- https://kb.isc.org/docs/aa-01567
- https://lists.debian.org/debian-lts-announce/2018/03/msg00015.html
- https://security.netapp.com/advisory/ntap-20250425-0010/
- https://usn.ubuntu.com/3586-1/
- https://usn.ubuntu.com/3586-2/
- https://www.debian.org/security/2018/dsa-4133
