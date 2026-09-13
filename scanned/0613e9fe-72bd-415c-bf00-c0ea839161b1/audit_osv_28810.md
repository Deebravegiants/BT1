# [M] mm/userfaultfd: reset ptes when close() for wr-protected ones

## Summary
Severity: Medium
Advisory: CVE-2024-36881
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36881
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/userfaultfd: reset ptes when close() for wr-protected ones

Userfaultfd unregister includes a step to remove wr-protect bits from all
the relevant pgtable entries, but that only covered an explicit
UFFDIO_UNREGISTER ioctl, not a close() on the userfaultfd itself.  Cover
that too.  This fixes a WARN trace.

The only user visible side effect is the user can observe leftover
wr-protect bits even if the user close()ed on an userfaultfd when
releasing the last reference of it.  However hopefully that should be
harmless, and nothing bad should happen even if so.

This change is now more important after the recent page-table-check
patch we merged in mm-unstable (446dd9ad37d0 ("mm/page_table_check:
support userfault wr-protect entries")), as we'll do sanity check on
uffd-wp bits without vma context.  So it's better if we can 100%
guarantee no uffd-wp bit leftovers, to make sure each report will be
valid.

## References
- https://git.kernel.org/stable/c/377f3a9a3d032a52325a5b110379a25dd1ab1931
- https://git.kernel.org/stable/c/8d8b68a5b0c9fb23d37df06bb273ead38fd5a29d
- https://git.kernel.org/stable/c/c88033efe9a391e72ba6b5df4b01d6e628f4e734
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36881.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
