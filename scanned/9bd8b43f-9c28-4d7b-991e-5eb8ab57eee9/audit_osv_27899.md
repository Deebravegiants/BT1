# [M] RDMA/srpt: Support specifying the srpt_service_guid parameter

## Summary
Severity: Medium
Advisory: CVE-2024-26744
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26744
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.19.308, >=4.20.0 <5.4.293, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/srpt: Support specifying the srpt_service_guid parameter

Make loading ib_srpt with this parameter set work. The current behavior is
that setting that parameter while loading the ib_srpt kernel module
triggers the following kernel crash:

BUG: kernel NULL pointer dereference, address: 0000000000000000
Call Trace:
 <TASK>
 parse_one+0x18c/0x1d0
 parse_args+0xe1/0x230
 load_module+0x8de/0xa60
 init_module_from_file+0x8b/0xd0
 idempotent_init_module+0x181/0x240
 __x64_sys_finit_module+0x5a/0xb0
 do_syscall_64+0x5f/0xe0
 entry_SYSCALL_64_after_hwframe+0x6e/0x76

## References
- https://git.kernel.org/stable/c/5a5c039dac1b1b7ba3e91c791f4421052bf79b82
- https://git.kernel.org/stable/c/84f1dac960cfa210a3b7a7522e6c2320ae91932b
- https://git.kernel.org/stable/c/989af2f29342a9a7c7515523d879b698ac8465f4
- https://git.kernel.org/stable/c/aee4dcfe17219fe60f2821923adea98549060af8
- https://git.kernel.org/stable/c/c99a827d3cff9f84e1cb997b7cc6386d107aa74d
- https://git.kernel.org/stable/c/e0055d6461b36bfc25a9d2ab974eef78d36a6738
- https://git.kernel.org/stable/c/fdfa083549de5d50ebf7f6811f33757781e838c0
- https://git.kernel.org/stable/c/fe2a73d57319feab4b3b175945671ce43492172f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26744.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26744
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
