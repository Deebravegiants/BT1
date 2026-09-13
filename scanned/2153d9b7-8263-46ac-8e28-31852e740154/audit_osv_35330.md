# [H] shmem: fix recovery on rename failures

## Summary
Severity: High
Advisory: CVE-2025-71072
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71072
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

shmem: fix recovery on rename failures

maple_tree insertions can fail if we are seriously short on memory;
simple_offset_rename() does not recover well if it runs into that.
The same goes for simple_offset_rename_exchange().

Moreover, shmem_whiteout() expects that if it succeeds, the caller will
progress to d_move(), i.e. that shmem_rename2() won't fail past the
successful call of shmem_whiteout().

Not hard to fix, fortunately - mtree_store() can't fail if the index we
are trying to store into is already present in the tree as a singleton.

For simple_offset_rename_exchange() that's enough - we just need to be
careful about the order of operations.

For simple_offset_rename() solution is to preinsert the target into the
tree for new_dir; the rest can be done without any potentially failing
operations.

That preinsertion has to be done in shmem_rename2() rather than in
simple_offset_rename() itself - otherwise we'd need to deal with the
possibility of failure after successful shmem_whiteout().

## References
- https://git.kernel.org/stable/c/4642686699a46718d7f2fb5acd1e9d866a9d9cca
- https://git.kernel.org/stable/c/4b0fe71fb3965d0db83cdfc2f4fe0b3227d70113
- https://git.kernel.org/stable/c/e1b4c6a58304fd490124cc2b454d80edc786665c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71072.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
