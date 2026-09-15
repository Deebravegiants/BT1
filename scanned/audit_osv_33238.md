# [C] smb: client: let smbd_destroy() call disable_work_sync(&info->post_send_credits_work)

## Summary
Severity: Critical
Advisory: CVE-2025-39932
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39932
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: let smbd_destroy() call disable_work_sync(&info->post_send_credits_work)

In smbd_destroy() we may destroy the memory so we better
wait until post_send_credits_work is no longer pending
and will never be started again.

I actually just hit the case using rxe:

WARNING: CPU: 0 PID: 138 at drivers/infiniband/sw/rxe/rxe_verbs.c:1032 rxe_post_recv+0x1ee/0x480 [rdma_rxe]
...
[ 5305.686979] [    T138]  smbd_post_recv+0x445/0xc10 [cifs]
[ 5305.687135] [    T138]  ? srso_alias_return_thunk+0x5/0xfbef5
[ 5305.687149] [    T138]  ? __kasan_check_write+0x14/0x30
[ 5305.687185] [    T138]  ? __pfx_smbd_post_recv+0x10/0x10 [cifs]
[ 5305.687329] [    T138]  ? __pfx__raw_spin_lock_irqsave+0x10/0x10
[ 5305.687356] [    T138]  ? srso_alias_return_thunk+0x5/0xfbef5
[ 5305.687368] [    T138]  ? srso_alias_return_thunk+0x5/0xfbef5
[ 5305.687378] [    T138]  ? _raw_spin_unlock_irqrestore+0x11/0x60
[ 5305.687389] [    T138]  ? srso_alias_return_thunk+0x5/0xfbef5
[ 5305.687399] [    T138]  ? get_receive_buffer+0x168/0x210 [cifs]
[ 5305.687555] [    T138]  smbd_post_send_credits+0x382/0x4b0 [cifs]
[ 5305.687701] [    T138]  ? __pfx_smbd_post_send_credits+0x10/0x10 [cifs]
[ 5305.687855] [    T138]  ? __pfx___schedule+0x10/0x10
[ 5305.687865] [    T138]  ? __pfx__raw_spin_lock_irq+0x10/0x10
[ 5305.687875] [    T138]  ? queue_delayed_work_on+0x8e/0xa0
[ 5305.687889] [    T138]  process_one_work+0x629/0xf80
[ 5305.687908] [    T138]  ? srso_alias_return_thunk+0x5/0xfbef5
[ 5305.687917] [    T138]  ? __kasan_check_write+0x14/0x30
[ 5305.687933] [    T138]  worker_thread+0x87f/0x1570
...

It means rxe_post_recv was called after rdma_destroy_qp().
This happened because put_receive_buffer() was triggered
by ib_drain_qp() and called:
queue_work(info->workqueue, &info->post_send_credits_work);

## References
- https://git.kernel.org/stable/c/3fabb1236f2e3ad78d531be0a4ad9f4a4ccdda87
- https://git.kernel.org/stable/c/6ae90a2baf923e85eb037b636aa641250bf4220f
- https://git.kernel.org/stable/c/d9dcbbcf9145b68aa85c40947311a6907277e097
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39932.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
