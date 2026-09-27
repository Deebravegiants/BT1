# [H] firmware: qcom: scm: Cleanup global '__scm' on probe failures

## Summary
Severity: High
Advisory: CVE-2024-57985
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57985
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: qcom: scm: Cleanup global '__scm' on probe failures

If SCM driver fails the probe, it should not leave global '__scm'
variable assigned, because external users of this driver will assume the
probe finished successfully.  For example TZMEM parts ('__scm->mempool')
are initialized later in the probe, but users of it (__scm_smc_call())
rely on the '__scm' variable.

This fixes theoretical NULL pointer exception, triggered via introducing
probe deferral in SCM driver with call trace:

  qcom_tzmem_alloc+0x70/0x1ac (P)
  qcom_tzmem_alloc+0x64/0x1ac (L)
  qcom_scm_assign_mem+0x78/0x194
  qcom_rmtfs_mem_probe+0x2d4/0x38c
  platform_probe+0x68/0xc8

## References
- https://git.kernel.org/stable/c/1e76b546e6fca7eb568161f408133904ca6bcf4f
- https://git.kernel.org/stable/c/390d3baeba51a126f75c97b90ec28b9384ce4b84
- https://git.kernel.org/stable/c/faf1715798fe72b79e4432ce8c6d03ca69765425
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57985.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57985
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
