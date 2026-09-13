# [M] CVE-2021-47363

## Summary
Severity: Medium
Advisory: CVE-2021-47363
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47363
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nexthop: Fix division by zero while replacing a resilient group

The resilient nexthop group torture tests in fib_nexthop.sh exposed a
possible division by zero while replacing a resilient group [1]. The
division by zero occurs when the data path sees a resilient nexthop
group with zero buckets.

The tests replace a resilient nexthop group in a loop while traffic is
forwarded through it. The tests do not specify the number of buckets
while performing the replacement, resulting in the kernel allocating a
stub resilient table (i.e, 'struct nh_res_table') with zero buckets.

This table should never be visible to the data path, but the old nexthop
group (i.e., 'oldg') might still be used by the data path when the stub
table is assigned to it.

Fix this by only assigning the stub table to the old nexthop group after
making sure the group is no longer used by the data path.

Tested with fib_nexthops.sh:

Tests passed: 222
Tests failed:   0

[1]
 divide error: 0000 [#1] PREEMPT SMP KASAN
 CPU: 0 PID: 1850 Comm: ping Not tainted 5.14.0-custom-10271-ga86eb53057fe #1107
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.14.0-4.fc34 04/01/2014
 RIP: 0010:nexthop_select_path+0x2d2/0x1a80
[...]
 Call Trace:
  fib_select_multipath+0x79b/0x1530
  fib_select_path+0x8fb/0x1c10
  ip_route_output_key_hash_rcu+0x1198/0x2da0
  ip_route_output_key_hash+0x190/0x340
  ip_route_output_flow+0x21/0x120
  raw_sendmsg+0x91d/0x2e10
  inet_sendmsg+0x9e/0xe0
  __sys_sendto+0x23d/0x360
  __x64_sys_sendto+0xe1/0x1b0
  do_syscall_64+0x35/0x80
  entry_SYSCALL_64_after_hwframe+0x44/0xae

## References
- https://git.kernel.org/stable/c/563f23b002534176f49524b5ca0e1d94d8906c40
- https://git.kernel.org/stable/c/e9d32ec26e7f01d1af13bdc687f586362546aa25
