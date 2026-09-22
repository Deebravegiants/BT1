# [M] vsock: Fix sk_error_queue memory leak

## Summary
Severity: Medium
Advisory: CVE-2024-53118
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53118
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: Fix sk_error_queue memory leak

Kernel queues MSG_ZEROCOPY completion notifications on the error queue.
Where they remain, until explicitly recv()ed. To prevent memory leaks,
clean up the queue when the socket is destroyed.

unreferenced object 0xffff8881028beb00 (size 224):
  comm "vsock_test", pid 1218, jiffies 4294694897
  hex dump (first 32 bytes):
    90 b0 21 17 81 88 ff ff 90 b0 21 17 81 88 ff ff  ..!.......!.....
    00 00 00 00 00 00 00 00 00 b0 21 17 81 88 ff ff  ..........!.....
  backtrace (crc 6c7031ca):
    [<ffffffff81418ef7>] kmem_cache_alloc_node_noprof+0x2f7/0x370
    [<ffffffff81d35882>] __alloc_skb+0x132/0x180
    [<ffffffff81d2d32b>] sock_omalloc+0x4b/0x80
    [<ffffffff81d3a8ae>] msg_zerocopy_realloc+0x9e/0x240
    [<ffffffff81fe5cb2>] virtio_transport_send_pkt_info+0x412/0x4c0
    [<ffffffff81fe6183>] virtio_transport_stream_enqueue+0x43/0x50
    [<ffffffff81fe0813>] vsock_connectible_sendmsg+0x373/0x450
    [<ffffffff81d233d5>] ____sys_sendmsg+0x365/0x3a0
    [<ffffffff81d246f4>] ___sys_sendmsg+0x84/0xd0
    [<ffffffff81d26f47>] __sys_sendmsg+0x47/0x80
    [<ffffffff820d3df3>] do_syscall_64+0x93/0x180
    [<ffffffff8220012b>] entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/bea4779a45f49275b1e1b1bd9de03cd3727244d8
- https://git.kernel.org/stable/c/fbf7085b3ad1c7cc0677834c90f985f1b4f77a33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53118.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53118
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
