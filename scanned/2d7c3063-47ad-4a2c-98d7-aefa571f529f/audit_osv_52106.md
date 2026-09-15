# [M] CVE-2021-47077

## Summary
Severity: Medium
Advisory: CVE-2021-47077
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2021-47077
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qedf: Add pointer checks in qedf_update_link_speed()

The following trace was observed:

 [   14.042059] Call Trace:
 [   14.042061]  <IRQ>
 [   14.042068]  qedf_link_update+0x144/0x1f0 [qedf]
 [   14.042117]  qed_link_update+0x5c/0x80 [qed]
 [   14.042135]  qed_mcp_handle_link_change+0x2d2/0x410 [qed]
 [   14.042155]  ? qed_set_ptt+0x70/0x80 [qed]
 [   14.042170]  ? qed_set_ptt+0x70/0x80 [qed]
 [   14.042186]  ? qed_rd+0x13/0x40 [qed]
 [   14.042205]  qed_mcp_handle_events+0x437/0x690 [qed]
 [   14.042221]  ? qed_set_ptt+0x70/0x80 [qed]
 [   14.042239]  qed_int_sp_dpc+0x3a6/0x3e0 [qed]
 [   14.042245]  tasklet_action_common.isra.14+0x5a/0x100
 [   14.042250]  __do_softirq+0xe4/0x2f8
 [   14.042253]  irq_exit+0xf7/0x100
 [   14.042255]  do_IRQ+0x7f/0xd0
 [   14.042257]  common_interrupt+0xf/0xf
 [   14.042259]  </IRQ>

API qedf_link_update() is getting called from QED but by that time
shost_data is not initialised. This results in a NULL pointer dereference
when we try to dereference shost_data while updating supported_speeds.

Add a NULL pointer check before dereferencing shost_data.

## References
- https://git.kernel.org/stable/c/11014efcec378bb0050a6cf08eaf375e3693400a
- https://git.kernel.org/stable/c/73578af92a0fae6609b955fcc9113e50e413c80f
- https://git.kernel.org/stable/c/a6362a737572f66051deb7637f3f77ddf7a4402f
