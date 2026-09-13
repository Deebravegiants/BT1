# [H] CVE-2025-20234

## Summary
Severity: High
Advisory: CVE-2025-20234
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-20234
Type: osv

## Details
A vulnerability in Universal Disk Format (UDF) processing of ClamAV could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device.

This vulnerability is due to a memory overread during UDF file scanning. An attacker could exploit this vulnerability by submitting a crafted file containing UDF content to be scanned by ClamAV on an affected device. A successful exploit could allow the attacker to terminate the ClamAV scanning process, resulting in a DoS condition on the affected software.
For a description of this vulnerability, see the .

## References
- https://blog.clamav.net/2025/06/clamav-143-and-109-security-patch.html
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-clamav-udf-hmwd9nDy
