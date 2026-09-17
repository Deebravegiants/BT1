# [H] scsi: qla2xxx: Fix crash when I/O abort times out

## Summary
Severity: High
Advisory: CVE-2022-50493
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2022-50493
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.258, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix crash when I/O abort times out

While performing CPU hotplug, a crash with the following stack was seen:

Call Trace:
     qla24xx_process_response_queue+0x42a/0x970 [qla2xxx]
     qla2x00_start_nvme_mq+0x3a2/0x4b0 [qla2xxx]
     qla_nvme_post_cmd+0x166/0x240 [qla2xxx]
     nvme_fc_start_fcp_op.part.0+0x119/0x2e0 [nvme_fc]
     blk_mq_dispatch_rq_list+0x17b/0x610
     __blk_mq_sched_dispatch_requests+0xb0/0x140
     blk_mq_sched_dispatch_requests+0x30/0x60
     __blk_mq_run_hw_queue+0x35/0x90
     __blk_mq_delay_run_hw_queue+0x161/0x180
     blk_execute_rq+0xbe/0x160
     __nvme_submit_sync_cmd+0x16f/0x220 [nvme_core]
     nvmf_connect_admin_queue+0x11a/0x170 [nvme_fabrics]
     nvme_fc_create_association.cold+0x50/0x3dc [nvme_fc]
     nvme_fc_connect_ctrl_work+0x19/0x30 [nvme_fc]
     process_one_work+0x1e8/0x3c0

On abort timeout, completion was called without checking if the I/O was
already completed.

Verify that I/O and abort request are indeed outstanding before attempting
completion.

## References
- https://git.kernel.org/stable/c/05382ed9142cf8a8a3fb662224477eecc415778b
- https://git.kernel.org/stable/c/5f730e489e741c28fe6a5b3308e33c094462acb0
- https://git.kernel.org/stable/c/68ad83188d782b2ecef2e41ac245d27e0710fe8e
- https://git.kernel.org/stable/c/cb4dff498468b62e8c520568559b3a9007e104d7
- https://git.kernel.org/stable/c/d3871af13aa03fbbe7fbb812eaf140501229a72e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50493.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50493
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
