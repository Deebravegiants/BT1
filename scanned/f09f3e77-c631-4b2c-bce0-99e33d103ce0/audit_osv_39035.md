# [C] scsi: qla2xxx: Completely fix fcport double free

## Summary
Severity: Critical
Advisory: CVE-2026-43414
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43414
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Completely fix fcport double free

In qla24xx_els_dcmd_iocb() sp->free is set to qla2x00_els_dcmd_sp_free().
When an error happens, this function is called by qla2x00_sp_release(),
when kref_put() releases the first and the last reference.

qla2x00_els_dcmd_sp_free() frees fcport by calling qla2x00_free_fcport().
Doing it one more time after kref_put() is a bad idea.

## References
- https://git.kernel.org/stable/c/c0b7da13a04bd70ef6070bfb9ea85f582294560a
- https://git.kernel.org/stable/c/d48ea85463f5b34f7b92ea0a13eddf1ab993da7b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
