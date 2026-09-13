# [M] can: af_can: fix NULL pointer dereference in can_rx_register()

## Summary
Severity: Medium
Advisory: CVE-2022-49863
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49863
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.12.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: af_can: fix NULL pointer dereference in can_rx_register()

It causes NULL pointer dereference when testing as following:
(a) use syscall(__NR_socket, 0x10ul, 3ul, 0) to create netlink socket.
(b) use syscall(__NR_sendmsg, ...) to create bond link device and vxcan
    link device, and bind vxcan device to bond device (can also use
    ifenslave command to bind vxcan device to bond device).
(c) use syscall(__NR_socket, 0x1dul, 3ul, 1) to create CAN socket.
(d) use syscall(__NR_bind, ...) to bind the bond device to CAN socket.

The bond device invokes the can-raw protocol registration interface to
receive CAN packets. However, ml_priv is not allocated to the dev,
dev_rcv_lists is assigned to NULL in can_rx_register(). In this case,
it will occur the NULL pointer dereference issue.

The following is the stack information:
BUG: kernel NULL pointer dereference, address: 0000000000000008
PGD 122a4067 P4D 122a4067 PUD 1223c067 PMD 0
Oops: 0000 [#1] PREEMPT SMP
RIP: 0010:can_rx_register+0x12d/0x1e0
Call Trace:
<TASK>
raw_enable_filters+0x8d/0x120
raw_enable_allfilters+0x3b/0x130
raw_bind+0x118/0x4f0
__sys_bind+0x163/0x1a0
__x64_sys_bind+0x1e/0x30
do_syscall_64+0x35/0x80
entry_SYSCALL_64_after_hwframe+0x63/0xcd
</TASK>

## References
- https://git.kernel.org/stable/c/261178a1c2623077d62e374a75c195e6c99a6f05
- https://git.kernel.org/stable/c/8aa59e355949442c408408c2d836e561794c40a1
- https://git.kernel.org/stable/c/a8055677b054bc2bb78beb1080fdc2dc5158c2fe
- https://git.kernel.org/stable/c/afab4655750fcb3fca359bc7d7214e3d634cdf9c
- https://git.kernel.org/stable/c/d68fa77ee3d03bad6fe84e89759ddf7005f9e9c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49863.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49863
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
