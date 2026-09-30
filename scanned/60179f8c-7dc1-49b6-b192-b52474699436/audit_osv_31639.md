# [C] CVE-2025-20260

## Summary
Severity: Critical
Advisory: CVE-2025-20260
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-20260
Type: osv

## Details
A vulnerability in the PDF scanning processes of ClamAV could allow an unauthenticated, remote attacker to cause a buffer overflow condition, cause a denial of service (DoS) condition, or execute arbitrary code on an affected device.

This vulnerability exists because memory buffers are allocated incorrectly when PDF files are processed. An attacker could exploit this vulnerability by submitting a crafted PDF file to be scanned by ClamAV on an affected device. A successful exploit could allow the attacker to trigger a buffer overflow, likely resulting in the termination of the ClamAV scanning process and a DoS condition on the affected software. Although unproven, there is also a possibility that an attacker could leverage the buffer overflow to execute arbitrary code with the privileges of the ClamAV process.

## References
- https://lists.debian.org/debian-lts-announce/2025/09/msg00006.html
- https://blog.clamav.net/2025/06/clamav-143-and-109-security-patch.html
