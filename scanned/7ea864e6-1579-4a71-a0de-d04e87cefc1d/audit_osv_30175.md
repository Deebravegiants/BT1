# [M] Bluetooth: bnep: fix wild-memory-access in proto_unregister

## Summary
Severity: Medium
Advisory: CVE-2024-50148
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50148
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: bnep: fix wild-memory-access in proto_unregister

There's issue as follows:
  KASAN: maybe wild-memory-access in range [0xdead...108-0xdead...10f]
  CPU: 3 UID: 0 PID: 2805 Comm: rmmod Tainted: G        W
  RIP: 0010:proto_unregister+0xee/0x400
  Call Trace:
   <TASK>
   __do_sys_delete_module+0x318/0x580
   do_syscall_64+0xc1/0x1d0
   entry_SYSCALL_64_after_hwframe+0x77/0x7f

As bnep_init() ignore bnep_sock_init()'s return value, and bnep_sock_init()
will cleanup all resource. Then when remove bnep module will call
bnep_sock_cleanup() to cleanup sock's resource.
To solve above issue just return bnep_sock_init()'s return value in
bnep_exit().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/03015b6329e6de42f03ec917c25c4cf944f81f66
- https://git.kernel.org/stable/c/20c424bc475b2b2a6e0e2225d2aae095c2ab2f41
- https://git.kernel.org/stable/c/2c439470b23d78095a0d2f923342df58b155f669
- https://git.kernel.org/stable/c/64a90991ba8d4e32e3173ddd83d0b24167a5668c
- https://git.kernel.org/stable/c/6c151aeb6dc414db8f4daf51be072e802fae6667
- https://git.kernel.org/stable/c/d10cd7bf574ead01fae140ce117a11bcdacbe6a8
- https://git.kernel.org/stable/c/e232728242c4e98fb30e4c6bedb6ba8b482b6301
- https://git.kernel.org/stable/c/fa58e23ea1359bd24b323916d191e2e9b4b19783
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50148.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50148
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
