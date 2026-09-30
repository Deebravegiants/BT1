# [H] bpf: Reject sleepable BPF_LSM_CGROUP programs at load time

## Summary
Severity: High
Advisory: CVE-2026-74338
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74338
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject sleepable BPF_LSM_CGROUP programs at load time

The cgroup shim runs under rcu_read_lock_dont_migrate(), so we should
not attach any sleepable BPF programs there. Add support to the verifier
to explicitly reject attempts to load sleepable BPF programs destined
for LSM cgroup attachment.

Without this, we get the following splat from a BPF_LSM_CGROUP
program marked BPF_F_SLEEPABLE attached to file_open when it calls
bpf_get_dentry_xattr():

  BUG: sleeping function called from invalid context at kernel/locking/rwsem.c:1567
  in_atomic(): 0, irqs_disabled(): 0, non_block: 0, pid: 34317, name: load
  preempt_count: 0, expected: 0
  RCU nest depth: 2, expected: 0
  Call Trace:
   down_read+0x76/0x480
   ext4_xattr_get+0x11f/0x700
   __vfs_getxattr+0xf0/0x150
   bpf_get_dentry_xattr+0xbb/0xf0
   bpf_prog_e76a298dac9218c6_test_open+0x6a/0x85
   __cgroup_bpf_run_lsm_current+0x326/0x840
   bpf_trampoline_6442534646+0x62/0x14d
   security_file_open+0x34/0x60
   do_dentry_open+0x340/0x1260
   vfs_open+0x7a/0x440
   path_openat+0x1bac/0x30a0

libbpf provides a .s named section variant for every sleepable
program type except lsm_cgroup, reflecting that per-cgroup LSM programs
are intended to only run in a non-sleepable context.

The above splat was obtained by bypassing libbpf by using bpf(2)
directly.

## References
- https://git.kernel.org/stable/c/5b038319be442c620f774e6fc9e9283deeca1c75
- https://git.kernel.org/stable/c/be9eaf2bb5db4ad3de61ef739fd268fd7f135737
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74338.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74338
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
