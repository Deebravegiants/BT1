# [M] CVE-2025-49604

## Summary
Severity: Medium
Advisory: CVE-2025-49604
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-49604
Type: osv

## Details
For Realtek AmebaD devices, a heap-based buffer overflow was discovered in Ameba-AIoT ameba-arduino-d before version 3.1.9 and ameba-rtos-d before commit c2bfd8216a1cbc19ad2ab5f48f372ecea756d67a on 2025/07/03. In the WLAN driver defragment function, lack of validation of the size of fragmented Wi-Fi frames may lead to a heap-based buffer overflow.

## References
- https://github.com/Ameba-AIoT/ameba-arduino-d/releases/tag/V3.1.9
- https://www.amebaiot.com/en/security-bulletin-cve-2025-49604/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49604.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49604
- https://github.com/Ameba-AIoT/ameba-arduino-d/pull/281
