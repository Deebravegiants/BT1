# [M] bpf: Fix memleak due to fentry attach failure

## Summary
Severity: Medium
Advisory: CVE-2023-53221
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53221
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix memleak due to fentry attach failure

If it fails to attach fentry, the allocated bpf trampoline image will be
left in the system. That can be verified by checking /proc/kallsyms.

This meamleak can be verified by a simple bpf program as follows:

  SEC("fentry/trap_init")
  int fentry_run()
  {
      return 0;
  }

It will fail to attach trap_init because this function is freed after
kernel init, and then we can find the trampoline image is left in the
system by checking /proc/kallsyms.

  $ tail /proc/kallsyms
  ffffffffc0613000 t bpf_trampoline_6442453466_1  [bpf]
  ffffffffc06c3000 t bpf_trampoline_6442453466_1  [bpf]

  $ bpftool btf dump file /sys/kernel/btf/vmlinux | grep "FUNC 'trap_init'"
  [2522] FUNC 'trap_init' type_id=119 linkage=static

  $ echo $((6442453466 & 0x7fffffff))
  2522

Note that there are two left bpf trampoline images, that is because the
libbpf will fallback to raw tracepoint if -EINVAL is returned.

## References
- https://git.kernel.org/stable/c/108598c39eefbedc9882273ac0df96127a629220
- https://git.kernel.org/stable/c/20109ddd5bea2c24d790debf5d02584ef24c3f5e
- https://git.kernel.org/stable/c/6aa27775db63ba8c7c73891c7dfb71ddc230c48d
- https://git.kernel.org/stable/c/f72c67d1a82dada7d6d504c806e111e913721a30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53221.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
