# [H] scsi: qla2xxx: Fix crash due to stale SRB access around I/O timeouts

## Summary
Severity: High
Advisory: CVE-2022-50098
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50098
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix crash due to stale SRB access around I/O timeouts

Ensure SRB is returned during I/O timeout error escalation. If that is not
possible fail the escalation path.

Following crash stack was seen:

BUG: unable to handle kernel paging request at 0000002f56aa90f8
IP: qla_chk_edif_rx_sa_delete_pending+0x14/0x30 [qla2xxx]
Call Trace:
 ? qla2x00_status_entry+0x19f/0x1c50 [qla2xxx]
 ? qla2x00_start_sp+0x116/0x1170 [qla2xxx]
 ? dma_pool_alloc+0x1d6/0x210
 ? mempool_alloc+0x54/0x130
 ? qla24xx_process_response_queue+0x548/0x12b0 [qla2xxx]
 ? qla_do_work+0x2d/0x40 [qla2xxx]
 ? process_one_work+0x14c/0x390

## References
- https://git.kernel.org/stable/c/7dcd49c42b14717dd668fd73b503d241fdf82439
- https://git.kernel.org/stable/c/b70553175d0f94ebd73670bc16ade90bd7f7d76f
- https://git.kernel.org/stable/c/b7bae3886a30d258b5b4fee26647043d68da3661
- https://git.kernel.org/stable/c/c39587bc0abaf16593f7abcdf8aeec3c038c7d52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50098.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50098
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
