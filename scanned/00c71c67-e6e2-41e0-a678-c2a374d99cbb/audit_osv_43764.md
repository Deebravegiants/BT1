# [H] vhost-scsi: reject feature changes after endpoint

## Summary
Severity: High
Advisory: CVE-2026-74702
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74702
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost-scsi: reject feature changes after endpoint

vhost_scsi_setup_vq_cmds() runs from VHOST_SCSI_SET_ENDPOINT and allocates
each command's protection scatterlist array (prot_sgl) according to the
acknowledged VIRTIO_SCSI_F_T10_PI bit.  The command pools are not rebuilt
when VHOST_SET_FEATURES changes that bit later.

Although virtio feature bits must not change after feature negotiation,
vhost_scsi_set_features() currently accepts such a request after the
endpoint is active and updates acked_features.  Enabling T10-PI after
endpoint setup therefore leaves prot_sgl NULL while the I/O path follows
the new feature bit.

For a 129-page protection payload, vhost_scsi_mapal() passes the missing
first chunk to sg_alloc_table_chained():

  sg_alloc_table_chained(table, 129, first_chunk=NULL,
                         nents_first_chunk=inline_sg_cnt)

sg_pool_index() then hits:

  BUG_ON(nents > SG_CHUNK_SIZE);   /* 129 > 128 */

The kernel reported the following call trace and register state:

  Call Trace:
   <TASK>
   ? __sg_alloc_table+0x1d8/0x250
   ? __pfx_vhost_run_work_list+0x10/0x10 [vhost]
   sg_alloc_table_chained+0x59/0xf0
   ? __pfx_sg_pool_alloc+0x10/0x10
   ? vhost_scsi_calc_sgls.constprop.0+0x43/0x60 [vhost_scsi]
   vhost_scsi_handle_vq+0xf02/0x1700 [vhost_scsi]
   ? __pfx_vhost_scsi_handle_vq+0x10/0x10 [vhost_scsi]
   vhost_scsi_handle_kick+0x37/0x50 [vhost_scsi]
   vhost_run_work_list+0x8e/0xd0 [vhost]
   vhost_task_fn+0xe1/0x210
   ret_from_fork+0x348/0x540
   </TASK>

  RIP: 0010:0x4
  CR2 = 0x4
  RSP: 0018:ffffc90000dbf940 EFLAGS: 00010202
  RAX: ffffffff82396810 RBX: ffff88811dc28b80 RCX: 0000000000000000
  RDX: 0000000000000000 RSI: 0000000000000820 RDI: 0000000000000081

VHOST_F_LOG_ALL is a vhost-specific runtime feature and remains the only
exception.

Reject changes to any feature other than VHOST_F_LOG_ALL while the
endpoint is active.  This preserves the existing runtime log toggle while
preventing feature-dependent command resources and data-path state from
becoming inconsistent.  Userspace must clear the endpoint before changing
any other negotiated feature and set the endpoint up again afterward.

## References
- https://git.kernel.org/stable/c/42bc45df5905e2b7dccb72adaf7730f66cfbe03f
- https://git.kernel.org/stable/c/9a3eb77a612f9d158e4d27df43677a014e9cfa55
- https://git.kernel.org/stable/c/a06e4611d45518896fbff4f45d9581578b107e91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74702.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74702
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
