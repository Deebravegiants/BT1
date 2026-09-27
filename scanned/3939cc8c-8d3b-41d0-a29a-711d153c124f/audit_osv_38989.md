# [H] mailbox: mchp-ipc-sbi: fix out-of-bounds access in mchp_ipc_get_cluster_aggr_irq()

## Summary
Severity: High
Advisory: CVE-2026-43274
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43274
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mailbox: mchp-ipc-sbi: fix out-of-bounds access in mchp_ipc_get_cluster_aggr_irq()

The cluster_cfg array is dynamically allocated to hold per-CPU
configuration structures, with its size based on the number of online
CPUs. Previously, this array was indexed using hartid, which may be
non-contiguous or exceed the bounds of the array, leading to
out-of-bounds access.
Switch to using cpuid as the index, as it is guaranteed to be within
the valid range provided by for_each_online_cpu().

## References
- https://git.kernel.org/stable/c/0442b6229e2eedc95a6d3d18ce75dec7f5b5377c
- https://git.kernel.org/stable/c/95438699c92947155823dcd3918049a07f3cd867
- https://git.kernel.org/stable/c/f7c330a8c83c9b0332fd524097eaf3e69148164d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43274.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
