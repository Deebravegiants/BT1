# [H] CVE-2024-20380

## Summary
Severity: High
Advisory: CVE-2024-20380
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2024-20380
Type: osv

## Details
A vulnerability in the HTML parser of ClamAV could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device.
The vulnerability is due to an issue in the C to Rust foreign function interface. An attacker could exploit this vulnerability by submitting a crafted file containing HTML content to be scanned by ClamAV on an affected device. An exploit could allow the attacker to cause the ClamAV scanning process to terminate, resulting in a DoS condition on the affected software.

## References
- https://blog.clamav.net/2024/04/clamav-131-123-106-patch-versions.html
