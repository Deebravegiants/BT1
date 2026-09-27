# [H] CVE-2026-20244

## Summary
Severity: High
Advisory: CVE-2026-20244
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-20244
Type: osv

## Details
A vulnerability in the DMG file format parser of ClamAV could allow an unauthenticated, remote attacker to cause a DoS condition, or possibly other expanded impacts, resulting from memory corruption on an affected device.

This vulnerability is due to improper boundary checks for content in DMG files during scanning, which may result in an integer overflow on 32-bit platforms only. An attacker could exploit this vulnerability by submitting a crafted file that contains DMG content to be scanned by ClamAV on an affected device. A successful exploit could allow the attacker to cause the ClamAV scanning process to terminate, resulting in a DoS condition on the affected software.

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-clamav-88cFYyxR
