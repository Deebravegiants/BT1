# [M] CVE-2024-20328

## Summary
Severity: Medium
Advisory: CVE-2024-20328
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2024-20328
Type: osv

## Details
A vulnerability in the VirusEvent feature of ClamAV could allow a local attacker to inject arbitrary commands with the privileges of the application service account.The vulnerability is due to unsafe handling of file names. A local attacker could exploit this vulnerability by supplying a file name containing command-line sequences. When processed on a system using configuration options for the VirusEvent feature, the attacker could cause the application to execute arbitrary commands.
ClamAV has released software updates that address this vulnerability. There are no workarounds that address this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5FXZYVDNV66RNMNVJOHAJAYRZV4U64CQ/
- https://blog.clamav.net/2023/11/clamav-130-122-105-released.html
