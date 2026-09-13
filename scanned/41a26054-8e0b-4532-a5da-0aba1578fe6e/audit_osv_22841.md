# [M] Azure RTOS FileX vulnerable to Buffer Offerflow

## Summary
Severity: Medium
Advisory: CVE-2022-39343
Aliases: GHSA-8jqf-wjhq-4w9f
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-11-08
Source: https://osv.dev/vulnerability/CVE-2022-39343
Type: osv

## Details
Azure RTOS FileX is a FAT-compatible file system that’s fully integrated with Azure RTOS ThreadX. In versions before 6.2.0, the Fault Tolerant feature of Azure RTOS FileX includes integer under and overflows which may be exploited to achieve buffer overflow and modify memory contents. When a valid log file with correct ID and checksum is detected by the `_fx_fault_tolerant_enable` function an attempt to recover the previous failed write operation is taken by call of `_fx_fault_tolerant_apply_logs`. This function iterates through the log entries and performs required recovery operations. When properly crafted a log including entries of type `FX_FAULT_TOLERANT_DIR_LOG_TYPE` may be utilized to introduce unexpected behavior. This issue has been patched in version 6.2.0. A workaround to fix line 218 in fx_fault_tolerant_apply_logs.c is documented in the GHSA.

## References
- https://github.com/azure-rtos/filex/blob/master/common/src/fx_fault_tolerant_apply_logs.c#L218
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39343.json
- https://github.com/azure-rtos/filex/security/advisories/GHSA-8jqf-wjhq-4w9f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39343
