# [H] CVE-2022-20803

## Summary
Severity: High
Advisory: CVE-2022-20803
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2022-20803
Type: osv

## Details
A vulnerability in the OLE2 file parser of Clam AntiVirus (ClamAV) versions 0.104.0 through 0.104.2 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device.The vulnerability is due to incorrect use of the realloc function that may result in a double-free. An attacker could exploit this vulnerability by submitting a crafted OLE2 file to be scanned by ClamAV on the affected device. An exploit could allow the attacker to cause the ClamAV scanning process to crash, resulting in a denial of service condition.

## References
- https://blog.clamav.net/2022/05/clamav-01050-01043-01036-released.html
- https://security.gentoo.org/glsa/202310-01
