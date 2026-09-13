# [M] scsi: lpfc: Move cfg_log_verbose check before calling lpfc_dmp_dbg()

## Summary
Severity: Medium
Advisory: CVE-2022-49542
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49542
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Move cfg_log_verbose check before calling lpfc_dmp_dbg()

In an attempt to log message 0126 with LOG_TRACE_EVENT, the following hard
lockup call trace hangs the system.

Call Trace:
 _raw_spin_lock_irqsave+0x32/0x40
 lpfc_dmp_dbg.part.32+0x28/0x220 [lpfc]
 lpfc_cmpl_els_fdisc+0x145/0x460 [lpfc]
 lpfc_sli_cancel_jobs+0x92/0xd0 [lpfc]
 lpfc_els_flush_cmd+0x43c/0x670 [lpfc]
 lpfc_els_flush_all_cmd+0x37/0x60 [lpfc]
 lpfc_sli4_async_event_proc+0x956/0x1720 [lpfc]
 lpfc_do_work+0x1485/0x1d70 [lpfc]
 kthread+0x112/0x130
 ret_from_fork+0x1f/0x40
Kernel panic - not syncing: Hard LOCKUP

The same CPU tries to claim the phba->port_list_lock twice.

Move the cfg_log_verbose checks as part of the lpfc_printf_vlog() and
lpfc_printf_log() macros before calling lpfc_dmp_dbg().  There is no need
to take the phba->port_list_lock within lpfc_dmp_dbg().

## References
- https://git.kernel.org/stable/c/09c772557a4fd9490fed1bfb133268313ea22213
- https://git.kernel.org/stable/c/271725e4028559ae7974d762a8467dc9de412f2e
- https://git.kernel.org/stable/c/cc6501afccec55b8b6c90584cbf71f1fefa77d1e
- https://git.kernel.org/stable/c/e294647b1aed4247fe52851f3a3b2b19ae906228
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49542.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49542
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
