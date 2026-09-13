# [C] Out of Bounds Write in FreeRTOS-Plus-TCP

## Summary
Severity: Critical
Advisory: CVE-2025-5688
Aliases: GHSA-5x4f-fvv8-wr65
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-06-04
Source: https://osv.dev/vulnerability/CVE-2025-5688
Type: osv

## Details
We have identified a buffer overflow issue allowing out-of-bounds write when processing LLMNR or mDNS queries with very long DNS names. This issue only affects systems using Buffer Allocation Scheme 1 with LLMNR or mDNS enabled.


Users should upgrade to the latest version and ensure any forked or derivative code is patched to incorporate the new fixes.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-012/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5688.json
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/security/advisories/GHSA-5x4f-fvv8-wr65
- https://nvd.nist.gov/vuln/detail/CVE-2025-5688
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.3.2
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP
