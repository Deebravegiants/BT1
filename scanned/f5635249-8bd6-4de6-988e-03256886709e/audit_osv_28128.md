# [H] Privilege Escalation in FreeRTOS Kernel ARMv7-M MPU ports and ARMv8-M ports with MPU support enabled

## Summary
Severity: High
Advisory: CVE-2024-28115
Aliases: GHSA-xcv7-v92w-gq6r
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-07
Source: https://osv.dev/vulnerability/CVE-2024-28115
Type: osv

## Details
FreeRTOS is a real-time operating system for microcontrollers. FreeRTOS Kernel versions through 10.6.1 do not sufficiently protect against local privilege escalation via Return Oriented Programming techniques should a vulnerability exist that allows code injection and execution. These issues affect ARMv7-M MPU ports, and ARMv8-M ports with Memory Protected Unit (MPU) support enabled (i.e. `configENABLE_MPU` set to 1). These issues are fixed in version 10.6.2 with a new MPU wrapper.

## References
- https://github.com/FreeRTOS/FreeRTOS-Kernel/releases/tag/V10.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28115.json
- https://github.com/FreeRTOS/FreeRTOS-Kernel/security/advisories/GHSA-xcv7-v92w-gq6r
- https://nvd.nist.gov/vuln/detail/CVE-2024-28115
