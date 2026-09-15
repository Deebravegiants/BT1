# [M] tipc: fix kernel warning when sending SYN message

## Summary
Severity: Medium
Advisory: CVE-2023-52700
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52700
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <6.1.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix kernel warning when sending SYN message

When sending a SYN message, this kernel stack trace is observed:

...
[   13.396352] RIP: 0010:_copy_from_iter+0xb4/0x550
...
[   13.398494] Call Trace:
[   13.398630]  <TASK>
[   13.398630]  ? __alloc_skb+0xed/0x1a0
[   13.398630]  tipc_msg_build+0x12c/0x670 [tipc]
[   13.398630]  ? shmem_add_to_page_cache.isra.71+0x151/0x290
[   13.398630]  __tipc_sendmsg+0x2d1/0x710 [tipc]
[   13.398630]  ? tipc_connect+0x1d9/0x230 [tipc]
[   13.398630]  ? __local_bh_enable_ip+0x37/0x80
[   13.398630]  tipc_connect+0x1d9/0x230 [tipc]
[   13.398630]  ? __sys_connect+0x9f/0xd0
[   13.398630]  __sys_connect+0x9f/0xd0
[   13.398630]  ? preempt_count_add+0x4d/0xa0
[   13.398630]  ? fpregs_assert_state_consistent+0x22/0x50
[   13.398630]  __x64_sys_connect+0x16/0x20
[   13.398630]  do_syscall_64+0x42/0x90
[   13.398630]  entry_SYSCALL_64_after_hwframe+0x63/0xcd

It is because commit a41dad905e5a ("iov_iter: saner checks for attempt
to copy to/from iterator") has introduced sanity check for copying
from/to iov iterator. Lacking of copy direction from the iterator
viewpoint would lead to kernel stack trace like above.

This commit fixes this issue by initializing the iov iterator with
the correct copy direction when sending SYN or ACK without data.

## References
- https://git.kernel.org/stable/c/11a4d6f67cf55883dc78e31c247d1903ed7feccc
- https://git.kernel.org/stable/c/54b6082aec178f16ad6d193b4ecdc9c4823d9a32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52700.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52700
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
