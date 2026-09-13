# [H] Integer wraparounds, under-allocations, and heap buffer overflows in Eclipse ThreadX xQueueCreate() and xQueueCreateSet()

## Summary
Severity: High
Advisory: CVE-2024-2212
Aliases: GHSA-v9jj-7qjg-h6g6
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-2212
Type: osv

## Details
In Eclipse ThreadX before 6.4.0,  xQueueCreate() and xQueueCreateSet() 
functions from the FreeRTOS compatibility API 
(utility/rtos_compatibility_layers/FreeRTOS/tx_freertos.c) were missing 
parameter checks. This could lead to integer wraparound, 
under-allocations and heap buffer overflows.

## References
- http://seclists.org/fulldisclosure/2024/May/35
- http://www.openwall.com/lists/oss-security/2024/05/28/1
- https://github.com/eclipse-threadx/threadx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2212.json
- https://github.com/eclipse-threadx/threadx/security/advisories/GHSA-v9jj-7qjg-h6g6
- https://nvd.nist.gov/vuln/detail/CVE-2024-2212
