# [C] Apache NuttX RTOS: NuttX Bluetooth Stack HCI and UART DoS/RCE Vulnerabilities.

## Summary
Severity: Critical
Advisory: CVE-2025-35003
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-26
Source: https://osv.dev/vulnerability/CVE-2025-35003
Type: osv

## Details
Improper Restriction of Operations within the Bounds of a Memory Buffer and Stack-based Buffer Overflow vulnerabilities were discovered in Apache NuttX RTOS Bluetooth Stack (HCI and UART components) that may result in system crash, denial of service, or arbitrary code execution, after receiving maliciously crafted packets.

NuttX's Bluetooth HCI/UART stack users are advised to upgrade to version 12.9.0, which fixes the identified implementation issues.

This issue affects Apache NuttX: from 7.25 before 12.9.0.

## References
- http://www.openwall.com/lists/oss-security/2025/05/26/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/35xxx/CVE-2025-35003.json
- https://lists.apache.org/thread/k4xzz3jhkx48zxw9vwmqrmm4hmg78vsj
- https://nvd.nist.gov/vuln/detail/CVE-2025-35003
- https://github.com/apache/nuttx/pull/16179
