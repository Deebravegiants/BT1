# [H] net: stmmac: Fix accessing freed irq affinity_hint

## Summary
Severity: High
Advisory: CVE-2025-23155
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23155
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.164, >=6.2.0 <6.6.117, >=6.7.0 <6.12.36, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: Fix accessing freed irq affinity_hint

In stmmac_request_irq_multi_msi(), a pointer to the stack variable
cpu_mask is passed to irq_set_affinity_hint(). This value is stored in
irq_desc->affinity_hint, but once stmmac_request_irq_multi_msi()
returns, the pointer becomes dangling.

The affinity_hint is exposed via procfs with S_IRUGO permissions,
allowing any unprivileged process to read it. Accessing this stale
pointer can lead to:

- a kernel oops or panic if the referenced memory has been released and
  unmapped, or
- leakage of kernel data into userspace if the memory is re-used for
  other purposes.

All platforms that use stmmac with PCI MSI (Intel, Loongson, etc) are
affected.

## References
- https://git.kernel.org/stable/c/2fbf67ddb8a0d0efc00d2df496a9843ec318d48b
- https://git.kernel.org/stable/c/442312c2a90d60c7a5197246583fa91d9e579985
- https://git.kernel.org/stable/c/960dab23f6d405740c537d095f90a4ee9ddd9285
- https://git.kernel.org/stable/c/9e51a6a44e2c4de780a26e8fe110d708e806a8cd
- https://git.kernel.org/stable/c/c60d101a226f18e9a8f01bb4c6ca2b47dfcb15ef
- https://git.kernel.org/stable/c/e148266e104fce396ad624079a6812ac3a9982ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23155.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
