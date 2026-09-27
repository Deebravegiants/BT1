# [C] lockd: Avoid hashing uninitialized bytes in nlm4svc_lookup_file()

## Summary
Severity: Critical
Advisory: CVE-2026-74315
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74315
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

lockd: Avoid hashing uninitialized bytes in nlm4svc_lookup_file()

file_hash() digests the first LOCKD_FH_HASH_SIZE bytes of
nfs_fh.data when bucketing nlm_files[], independent of fh.size.
Commit 3de744ee4e45 ("lockd: Use xdrgen XDR functions for the
NLMv4 TEST procedure") set .pc_argzero to zero for the converted
procedures and moved file-handle population into
nlm4svc_lookup_file(), which copies only xdr_lock->fh.len bytes
into lock->fh.data.

When an NLMv4 client presents a file handle shorter than
LOCKD_FH_HASH_SIZE, bytes fh.len..31 retain whatever the argument
buffer held from an earlier request.  The same wire handle then
hashes to different buckets across calls; nlm_lookup_file() misses
the existing nlm_file entry, and lock-state lookups fail.

Zero only the tail bytes that file_hash() would otherwise consume.
Handles of LOCKD_FH_HASH_SIZE or larger already populate every byte
that file_hash() reads.

## References
- https://git.kernel.org/stable/c/686c2434f9f16b87aeed18d76cc562df9f2695ab
- https://git.kernel.org/stable/c/6e4c62caecf792e8a15ad9bc7f371e57c17e3302
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74315.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74315
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
