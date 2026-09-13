# [C] RDMA/siw: Add sendpage_ok() check to disable MSG_SPLICE_PAGES

## Summary
Severity: Critical
Advisory: CVE-2024-53094
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-53094
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.6.62, >=6.7.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Add sendpage_ok() check to disable MSG_SPLICE_PAGES

While running ISER over SIW, the initiator machine encounters a warning
from skb_splice_from_iter() indicating that a slab page is being used in
send_page. To address this, it is better to add a sendpage_ok() check
within the driver itself, and if it returns 0, then MSG_SPLICE_PAGES flag
should be disabled before entering the network stack.

A similar issue has been discussed for NVMe in this thread:
https://lore.kernel.org/all/20240530142417.146696-1-ofir.gal@volumez.com/

  WARNING: CPU: 0 PID: 5342 at net/core/skbuff.c:7140 skb_splice_from_iter+0x173/0x320
  Call Trace:
   tcp_sendmsg_locked+0x368/0xe40
   siw_tx_hdt+0x695/0xa40 [siw]
   siw_qp_sq_process+0x102/0xb00 [siw]
   siw_sq_resume+0x39/0x110 [siw]
   siw_run_sq+0x74/0x160 [siw]
   kthread+0xd2/0x100
   ret_from_fork+0x34/0x40
   ret_from_fork_asm+0x1a/0x30

## References
- https://git.kernel.org/stable/c/3406bfc813a9bbd9c3055795e985f527b7852e8c
- https://git.kernel.org/stable/c/4e1e3dd88a4cedd5ccc1a3fc3d71e03b70a7a791
- https://git.kernel.org/stable/c/bb5738957d92c8603a90c9664d34236641c221b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53094.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53094
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
