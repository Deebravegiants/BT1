# [H] CVE-2026-0648

## Summary
Severity: High
Advisory: CVE-2026-0648
Aliases: GHSA-xj75-fc68-h4rw
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-0648
Type: osv

## Details
The vulnerability stems from an incorrect error-checking logic in the CreateCounter() function (in threadx/utility/rtos_compatibility_layers/OSEK/tx_osek.c) when handling the return value of osek_get_counter(). Specifically, the current code checks if cntr_id equals 0u to determine failure, but @osek_get_counter() actually returns E_OS_SYS_STACK (defined as 12U) when it fails. This mismatch causes the error branch to never execute even when the counter pool is exhausted.

As a result, when the counter pool is depleted, the code proceeds to cast the error code (12U) to a pointer (OSEK_COUNTER *), creating a wild pointer. Subsequent writes to members of this pointer lead to writes to illegal memory addresses (e.g., 0x0000000C), which can trigger immediate HardFaults or silent memory corruption.

This vulnerability poses significant risks, including potential denial-of-service attacks (via repeated calls to exhaust the counter pool) and unauthorized memory access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0648.json
- https://github.com/eclipse-threadx/threadx/security/advisories/GHSA-xj75-fc68-h4rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-0648
- https://github.com/eclipse-threadx/threadx
