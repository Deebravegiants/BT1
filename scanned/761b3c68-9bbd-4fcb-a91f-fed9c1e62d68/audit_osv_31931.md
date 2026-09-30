# [M] mm/huge_memory: drop beyond-EOF folios with the right number of refs

## Summary
Severity: Medium
Advisory: CVE-2025-22000
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22000
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/huge_memory: drop beyond-EOF folios with the right number of refs

When an after-split folio is large and needs to be dropped due to EOF,
folio_put_refs(folio, folio_nr_pages(folio)) should be used to drop all
page cache refs.  Otherwise, the folio will not be freed, causing memory
leak.

This leak would happen on a filesystem with blocksize > page_size and a
truncate is performed, where the blocksize makes folios split to >0 order
ones, causing truncated folios not being freed.

## References
- https://git.kernel.org/stable/c/14efb4793519d73fb2902bb0ece319b886e4b4b9
- https://git.kernel.org/stable/c/86368616a9ce51f6b41efa251b6e066893851d67
- https://git.kernel.org/stable/c/92ad820a1f2d95d5a8d6c2bd3f391bbb068a5f9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22000.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22000
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
