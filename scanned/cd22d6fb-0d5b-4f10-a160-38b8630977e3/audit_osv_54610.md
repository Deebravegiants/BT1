# [H] CVE-2024-20290

## Summary
Severity: High
Advisory: CVE-2024-20290
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-07
Source: https://osv.dev/vulnerability/CVE-2024-20290
Type: osv

## Details
A vulnerability in the OLE2 file format parser of ClamAV could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device.
 This vulnerability is due to an incorrect check for end-of-string values during scanning, which may result in a heap buffer over-read. An attacker could exploit this vulnerability by submitting a crafted file containing OLE2 content to be scanned by ClamAV on an affected device. A successful exploit could allow the attacker to cause the ClamAV scanning process to terminate, resulting in a DoS condition on the affected software and consuming available system resources.
 For a description of this vulnerability, see the ClamAV blog .

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-clamav-hDffu6t
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6MUDUPAHAAV6FPB2C2QIQCFJ4SHYBOTY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5FXZYVDNV66RNMNVJOHAJAYRZV4U64CQ/
