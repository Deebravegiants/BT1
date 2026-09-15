# [H] CVE-2023-20212

## Summary
Severity: High
Advisory: CVE-2023-20212
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-18
Source: https://osv.dev/vulnerability/CVE-2023-20212
Type: osv

## Details
A vulnerability in the AutoIt module of ClamAV could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. 
 This vulnerability is due to a logic error in the memory management of an affected device. An attacker could exploit this vulnerability by submitting a crafted AutoIt file to be scanned by ClamAV on the affected device. A successful exploit could allow the attacker to cause the ClamAV scanning process to restart unexpectedly, resulting in a DoS condition.

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-clamav-dos-FTkhqMWZ
