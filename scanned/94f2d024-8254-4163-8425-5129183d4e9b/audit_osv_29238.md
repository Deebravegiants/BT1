# [H] mm: vmalloc: check if a hash-index is in cpu_possible_mask

## Summary
Severity: High
Advisory: CVE-2024-41032
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41032
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: vmalloc: check if a hash-index is in cpu_possible_mask

The problem is that there are systems where cpu_possible_mask has gaps
between set CPUs, for example SPARC.  In this scenario addr_to_vb_xa()
hash function can return an index which accesses to not-possible and not
setup CPU area using per_cpu() macro.  This results in an oops on SPARC.

A per-cpu vmap_block_queue is also used as hash table, incorrectly
assuming the cpu_possible_mask has no gaps.  Fix it by adjusting an index
to a next possible CPU.

## References
- https://git.kernel.org/stable/c/28acd531c9a365dac01b32e6bc54aed8c1429bcb
- https://git.kernel.org/stable/c/47f9b6e49b422392fb0e348a65eb925103ba1882
- https://git.kernel.org/stable/c/a34acf30b19bc4ee3ba2f1082756ea2604c19138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41032.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41032
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
