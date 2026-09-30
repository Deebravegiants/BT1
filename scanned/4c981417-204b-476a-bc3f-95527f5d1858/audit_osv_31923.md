# [H] x86/microcode/AMD: Fix out-of-bounds on systems with CPU-less NUMA nodes

## Summary
Severity: High
Advisory: CVE-2025-21991
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-21991
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.3.0 <6.12.20, >=6.7.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/microcode/AMD: Fix out-of-bounds on systems with CPU-less NUMA nodes

Currently, load_microcode_amd() iterates over all NUMA nodes, retrieves their
CPU masks and unconditionally accesses per-CPU data for the first CPU of each
mask.

According to Documentation/admin-guide/mm/numaperf.rst:

  "Some memory may share the same node as a CPU, and others are provided as
  memory only nodes."

Therefore, some node CPU masks may be empty and wouldn't have a "first CPU".

On a machine with far memory (and therefore CPU-less NUMA nodes):
- cpumask_of_node(nid) is 0
- cpumask_first(0) is CONFIG_NR_CPUS
- cpu_data(CONFIG_NR_CPUS) accesses the cpu_info per-CPU array at an
  index that is 1 out of bounds

This does not have any security implications since flashing microcode is
a privileged operation but I believe this has reliability implications by
potentially corrupting memory while flashing a microcode update.

When booting with CONFIG_UBSAN_BOUNDS=y on an AMD machine that flashes
a microcode update. I get the following splat:

  UBSAN: array-index-out-of-bounds in arch/x86/kernel/cpu/microcode/amd.c:X:Y
  index 512 is out of range for type 'unsigned long[512]'
  [...]
  Call Trace:
   dump_stack
   __ubsan_handle_out_of_bounds
   load_microcode_amd
   request_microcode_amd
   reload_store
   kernfs_fop_write_iter
   vfs_write
   ksys_write
   do_syscall_64
   entry_SYSCALL_64_after_hwframe

Change the loop to go over only NUMA nodes which have CPUs before determining
whether the first CPU on the respective node needs microcode update.

  [ bp: Massage commit message, fix typo. ]

## References
- https://git.kernel.org/stable/c/18b5d857c6496b78ead2fd10001b81ae32d30cac
- https://git.kernel.org/stable/c/488ffc0cac38f203979f83634236ee53251ce593
- https://git.kernel.org/stable/c/5ac295dfccb5b015493f86694fa13a0dde4d3665
- https://git.kernel.org/stable/c/985a536e04bbfffb1770df43c6470f635a6b1073
- https://git.kernel.org/stable/c/d509c4731090ebd9bbdb72c70a2d70003ae81f4f
- https://git.kernel.org/stable/c/e3e89178a9f4a80092578af3ff3c8478f9187d59
- https://git.kernel.org/stable/c/e686349cc19e800dac8971929089ba5ff59abfb0
- https://git.kernel.org/stable/c/ec52240622c4d218d0240079b7c1d3ec2328a9f4
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21991.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
