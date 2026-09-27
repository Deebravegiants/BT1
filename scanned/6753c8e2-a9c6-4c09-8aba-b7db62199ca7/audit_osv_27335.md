# [H] CVE-2024-20505

## Summary
Severity: High
Advisory: CVE-2024-20505
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-20505
Type: osv

## Details
A vulnerability in the PDF parsing module of Clam AntiVirus (ClamAV) versions 1.4.0, 1.3.2 and prior versions, all 1.2.x versions, 1.0.6 and prior versions, all 0.105.x versions, all 0.104.x versions, and 0.103.11 and all prior versions could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device.

The vulnerability is due to an out of bounds read. An attacker could exploit this vulnerability by submitting a crafted PDF file to be scanned by ClamAV on an affected device. An exploit could allow the attacker to terminate the scanning process.

## References
- https://lists.debian.org/debian-lts-announce/2024/12/msg00004.html
- https://blog.clamav.net/2024/09/clamav-141-132-107-and-010312-security.html
