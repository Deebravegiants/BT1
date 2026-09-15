# [H] xprtrdma: treat all calls not a bcall when bc_serv is NULL

## Summary
Severity: High
Advisory: CVE-2022-49321
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49321
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: treat all calls not a bcall when bc_serv is NULL

When a rdma server returns a fault format reply, nfs v3 client may
treats it as a bcall when bc service is not exist.

The debug message at rpcrdma_bc_receive_call are,

[56579.837169] RPC:       rpcrdma_bc_receive_call: callback XID
00000001, length=20
[56579.837174] RPC:       rpcrdma_bc_receive_call: 00 00 00 01 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 04

After that, rpcrdma_bc_receive_call will meets NULL pointer as,

[  226.057890] BUG: unable to handle kernel NULL pointer dereference at
00000000000000c8
...
[  226.058704] RIP: 0010:_raw_spin_lock+0xc/0x20
...
[  226.059732] Call Trace:
[  226.059878]  rpcrdma_bc_receive_call+0x138/0x327 [rpcrdma]
[  226.060011]  __ib_process_cq+0x89/0x170 [ib_core]
[  226.060092]  ib_cq_poll_work+0x26/0x80 [ib_core]
[  226.060257]  process_one_work+0x1a7/0x360
[  226.060367]  ? create_worker+0x1a0/0x1a0
[  226.060440]  worker_thread+0x30/0x390
[  226.060500]  ? create_worker+0x1a0/0x1a0
[  226.060574]  kthread+0x116/0x130
[  226.060661]  ? kthread_flush_work_fn+0x10/0x10
[  226.060724]  ret_from_fork+0x35/0x40
...

## References
- https://git.kernel.org/stable/c/11270e7ca268e8d61b5d9e5c3a54bd1550642c9c
- https://git.kernel.org/stable/c/8dbae5affbdbf524b48000f9d357925bb001e5f4
- https://git.kernel.org/stable/c/8e3943c50764dc7c5f25911970c3ff062ec1f18c
- https://git.kernel.org/stable/c/90c4f73104016748533a5707ecd15930fbeff402
- https://git.kernel.org/stable/c/91784f3d77b73885e1b2e6b59d3cbf0de0a1126a
- https://git.kernel.org/stable/c/998d35a2aff4b81a1c784f3aa45cd3afff6814c1
- https://git.kernel.org/stable/c/a3fc8051ee061e31db13e2fe011e8e0b71a7f815
- https://git.kernel.org/stable/c/da99331fa62131a38a0947a8204c5208de7b0454
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49321.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
