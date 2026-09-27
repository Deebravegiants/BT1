# [H] CVE-2025-20128

## Summary
Severity: High
Advisory: CVE-2025-20128
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2025-20128
Type: osv

## Details
A vulnerability in the Object Linking and Embedding 2 (OLE2) decryption routine of ClamAV could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device.

This vulnerability is due to an integer underflow in a bounds check that allows for a heap buffer overflow read. An attacker could exploit this vulnerability by submitting a crafted file containing OLE2 content to be scanned by ClamAV on an affected device. A successful exploit could allow the attacker to terminate the ClamAV scanning process, resulting in a DoS condition on the affected software.
For a description of this vulnerability, see the .
Cisco has released software updates that address this vulnerability. There are no workarounds that address this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/09/msg00006.html
- https://blog.clamav.net/2025/01/clamav-142-and-108-security-patch.html
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-clamav-ole2-H549rphA
