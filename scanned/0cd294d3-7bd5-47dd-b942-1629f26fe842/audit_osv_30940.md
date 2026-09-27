# [M] bpf: Fix bpf_get_smp_processor_id() on !CONFIG_SMP

## Summary
Severity: Medium
Advisory: CVE-2024-56768
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-56768
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix bpf_get_smp_processor_id() on !CONFIG_SMP

On x86-64 calling bpf_get_smp_processor_id() in a kernel with CONFIG_SMP
disabled can trigger the following bug, as pcpu_hot is unavailable:

 [    8.471774] BUG: unable to handle page fault for address: 00000000936a290c
 [    8.471849] #PF: supervisor read access in kernel mode
 [    8.471881] #PF: error_code(0x0000) - not-present page

Fix by inlining a return 0 in the !CONFIG_SMP case.

## References
- https://git.kernel.org/stable/c/23579010cf0a12476e96a5f1acdf78a9c5843657
- https://git.kernel.org/stable/c/f4ab7d74247b0150547cf909b3f6f24ee85183df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56768.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56768
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
