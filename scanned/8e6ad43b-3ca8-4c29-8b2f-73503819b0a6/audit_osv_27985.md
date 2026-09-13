# [H] netfilter: nf_tables: release mutex after nft_gc_seq_end from abort path

## Summary
Severity: High
Advisory: CVE-2024-26925
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-24
Source: https://osv.dev/vulnerability/CVE-2024-26925
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.155, >=5.16.0 <6.1.86, >=6.2.0 <6.6.26, >=6.5.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: release mutex after nft_gc_seq_end from abort path

The commit mutex should not be released during the critical section
between nft_gc_seq_begin() and nft_gc_seq_end(), otherwise, async GC
worker could collect expired objects and get the released commit lock
within the same GC sequence.

nf_tables_module_autoload() temporarily releases the mutex to load
module dependencies, then it goes back to replay the transaction again.
Move it at the end of the abort phase after nft_gc_seq_end() is called.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-354112.html
- https://git.kernel.org/stable/c/0d459e2ffb541841714839e8228b845458ed3b27
- https://git.kernel.org/stable/c/2cee2ff7f8cce12a63a0a23ffe27f08d99541494
- https://git.kernel.org/stable/c/61ac7284346c32f9a8c8ceac56102f7914060428
- https://git.kernel.org/stable/c/8038ee3c3e5b59bcd78467686db5270c68544e30
- https://git.kernel.org/stable/c/8d3a58af50e46167b6f1db47adadad03c0045dae
- https://git.kernel.org/stable/c/a34ba4bdeec0c3b629160497594908dc820110f1
- https://git.kernel.org/stable/c/eb769ff4e281f751adcaf4f4445cbf30817be139
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26925.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
