# [H] erofs: fix managed cache race for unaligned extents

## Summary
Severity: High
Advisory: CVE-2026-64031
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64031
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix managed cache race for unaligned extents

After unaligned compressed extents were introduced, the following race
could occur:

[Thread 1]                                   [Thread 2]
(z_erofs_fill_bio_vec)
<handle a Z_EROFS_PREALLOCATED_FOLIO folio>
...
filemap_add_folio (1)
                                             (z_erofs_bind_cache)
                                             <the same folio is found..>
                                             ..
                                             ..
folio_attach_private (2)
                                             filemap_add_folio (3) again

Since (1) is executed but (2) hasn't been executed yet, it's possible
that another thread finds the same managed folio in z_erofs_bind_cache()
for a different pcluster and calls filemap_add_folio() again since
folio->private is still Z_EROFS_PREALLOCATED_FOLIO.

Fix this by explicitly clearing folio->private before making the folio
visible in the managed cache so that another pcluster can simply wait
on the locked managed folio as what we did for other shared cases [1].

This only impacts unaligned data compression (`-E48bit` with zstd,
for example).

[1] Commit 9e2f9d34dd12 ("erofs: handle overlapped pclusters out of
 crafted images properly") was originally introduced to handle crafted
 overlapped extents, but it addresses unaligned extents as well.

## References
- https://git.kernel.org/stable/c/038166f873c4caf6e85cfd4ea0c5a5ba297b4e8b
- https://git.kernel.org/stable/c/425d32d6288d7d845e486af9419bbedccd8c9103
- https://git.kernel.org/stable/c/649932fc3815eda2f24eb4de4b3a5e94886ee0b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64031.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64031
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
