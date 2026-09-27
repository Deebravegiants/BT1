# [H] CVE-2026-20216

## Summary
Severity: High
Advisory: CVE-2026-20216
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-20216
Type: osv

## Details
A vulnerability in the InstallShield file format parser of ClamAV could allow an unauthenticated, remote attacker to cause a DoS condition on an affected device.

This vulnerability is due to improper handling of temporary resources during file scanning. An attacker could exploit this vulnerability by submitting a crafted InstallShield file to be scanned by ClamAV on an affected device. A successful exploit could allow the attacker to terminate the ClamAV scanning process and temporarily consume available system resources, resulting in a DoS condition on the affected software.

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-clamav-88cFYyxR
