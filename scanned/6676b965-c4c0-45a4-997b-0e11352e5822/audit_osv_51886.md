# [H] CVE-2021-4439

## Summary
Severity: High
Advisory: CVE-2021-4439
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2021-4439
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

isdn: cpai: check ctr->cnr to avoid array index out of bound

The cmtp_add_connection() would add a cmtp session to a controller
and run a kernel thread to process cmtp.

	__module_get(THIS_MODULE);
	session->task = kthread_run(cmtp_session, session, "kcmtpd_ctr_%d",
								session->num);

During this process, the kernel thread would call detach_capi_ctr()
to detach a register controller. if the controller
was not attached yet, detach_capi_ctr() would
trigger an array-index-out-bounds bug.

[   46.866069][ T6479] UBSAN: array-index-out-of-bounds in
drivers/isdn/capi/kcapi.c:483:21
[   46.867196][ T6479] index -1 is out of range for type 'capi_ctr *[32]'
[   46.867982][ T6479] CPU: 1 PID: 6479 Comm: kcmtpd_ctr_0 Not tainted
5.15.0-rc2+ #8
[   46.869002][ T6479] Hardware name: QEMU Standard PC (i440FX + PIIX,
1996), BIOS 1.14.0-2 04/01/2014
[   46.870107][ T6479] Call Trace:
[   46.870473][ T6479]  dump_stack_lvl+0x57/0x7d
[   46.870974][ T6479]  ubsan_epilogue+0x5/0x40
[   46.871458][ T6479]  __ubsan_handle_out_of_bounds.cold+0x43/0x48
[   46.872135][ T6479]  detach_capi_ctr+0x64/0xc0
[   46.872639][ T6479]  cmtp_session+0x5c8/0x5d0
[   46.873131][ T6479]  ? __init_waitqueue_head+0x60/0x60
[   46.873712][ T6479]  ? cmtp_add_msgpart+0x120/0x120
[   46.874256][ T6479]  kthread+0x147/0x170
[   46.874709][ T6479]  ? set_kthread_struct+0x40/0x40
[   46.875248][ T6479]  ret_from_fork+0x1f/0x30
[   46.875773][ T6479]

## References
- https://git.kernel.org/stable/c/24219a977bfe3d658687e45615c70998acdbac5a
- https://git.kernel.org/stable/c/285e9210b1fab96a11c0be3ed5cea9dd48b6ac54
- https://git.kernel.org/stable/c/7d91adc0ccb060ce564103315189466eb822cc6a
- https://git.kernel.org/stable/c/7f221ccbee4ec662e2292d490a43ce6c314c4594
- https://git.kernel.org/stable/c/9b6b2db77bc3121fe435f1d4b56e34de443bec75
- https://git.kernel.org/stable/c/cc20226e218a2375d50dd9ac14fb4121b43375ff
- https://git.kernel.org/stable/c/e8b8de17e164c9f1b7777f1c6f99d05539000036
- https://git.kernel.org/stable/c/1f3e2e97c003f80c4b087092b225c8787ff91e4d
