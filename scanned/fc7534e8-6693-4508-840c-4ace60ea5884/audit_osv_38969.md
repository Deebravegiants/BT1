# [H] LoongArch: Make cpumask_of_node() robust against NUMA_NO_NODE

## Summary
Severity: High
Advisory: CVE-2026-43212
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43212
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: Make cpumask_of_node() robust against NUMA_NO_NODE

The arch definition of cpumask_of_node() cannot handle NUMA_NO_NODE -
which is a valid index - so add a check for this.

## References
- https://git.kernel.org/stable/c/1d8f2f024801019d85159a020b72a4424b46bcf4
- https://git.kernel.org/stable/c/61a56df2fbaad3a4d00f0c6a904b5d1ee8982eb4
- https://git.kernel.org/stable/c/92adfb707beec0fe956424373654a70aad35ea13
- https://git.kernel.org/stable/c/94b0c831eda778ae9e4f2164a8b3de485d8977bb
- https://git.kernel.org/stable/c/b5bf05e05cdf489a04137e4da407de9d4cca5295
- https://git.kernel.org/stable/c/bb1a54f7f011f19ed936632698eae574e0b91063
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43212.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
