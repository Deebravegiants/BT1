# [H] dma-mapping: benchmark: handle NUMA_NO_NODE correctly

## Summary
Severity: High
Advisory: CVE-2024-39277
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-39277
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-mapping: benchmark: handle NUMA_NO_NODE correctly

cpumask_of_node() can be called for NUMA_NO_NODE inside do_map_benchmark()
resulting in the following sanitizer report:

UBSAN: array-index-out-of-bounds in ./arch/x86/include/asm/topology.h:72:28
index -1 is out of range for type 'cpumask [64][1]'
CPU: 1 PID: 990 Comm: dma_map_benchma Not tainted 6.9.0-rc6 #29
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
Call Trace:
 <TASK>
dump_stack_lvl (lib/dump_stack.c:117)
ubsan_epilogue (lib/ubsan.c:232)
__ubsan_handle_out_of_bounds (lib/ubsan.c:429)
cpumask_of_node (arch/x86/include/asm/topology.h:72) [inline]
do_map_benchmark (kernel/dma/map_benchmark.c:104)
map_benchmark_ioctl (kernel/dma/map_benchmark.c:246)
full_proxy_unlocked_ioctl (fs/debugfs/file.c:333)
__x64_sys_ioctl (fs/ioctl.c:890)
do_syscall_64 (arch/x86/entry/common.c:83)
entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)

Use cpumask_of_node() in place when binding a kernel thread to a cpuset
of a particular node.

Note that the provided node id is checked inside map_benchmark_ioctl().
It's just a NUMA_NO_NODE case which is not handled properly later.

Found by Linux Verification Center (linuxtesting.org).

## References
- https://git.kernel.org/stable/c/50ee21bfc005e69f183d6b4b454e33f0c2571e1f
- https://git.kernel.org/stable/c/5a91116b003175302f2e6ad94b76fb9b5a141a41
- https://git.kernel.org/stable/c/8e1ba9df9a35e8dc64f657a64e523c79ba01e464
- https://git.kernel.org/stable/c/b41b0018e8ca06e985e87220a618ec633988fd13
- https://git.kernel.org/stable/c/e64746e74f717961250a155e14c156616fcd981f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39277.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
