# [M] CVE-2019-1798

## Summary
Severity: Medium
Advisory: CVE-2019-1798
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-1798
Type: osv

## Details
A vulnerability in the Portable Executable (PE) file scanning functionality of Clam AntiVirus (ClamAV) Software versions 0.101.1 and prior could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a lack of proper input and validation checking mechanisms for PE files sent an affected device. An attacker could exploit this vulnerability by sending malformed PE files to the device running an affected version ClamAV Software. An exploit could allow the attacker to cause an out-of-bounds read condition, resulting in a crash that could result in a denial of service condition on an affected device.

## References
- https://security.gentoo.org/glsa/201904-12
- https://bugzilla.clamav.net/show_bug.cgi?id=12262
