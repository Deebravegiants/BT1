# [M] Stack-based Buffer Overflow in libmodbus library

## Summary
Severity: Medium
Advisory: CVE-2024-10918
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-10918
Type: osv

## Details
Stack-based Buffer Overflow vulnerability in libmodbus v3.1.10 allows to overflow the buffer allocated for the Modbus response if the function tries to reply to a Modbus request with an
unexpected length.

## References
- https://libmodbus.org/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2026/08/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10918.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10918
- https://www.nozominetworks.com/labs/vulnerability-advisories-cve-2024-10918
- https://github.com/stephane/libmodbus
