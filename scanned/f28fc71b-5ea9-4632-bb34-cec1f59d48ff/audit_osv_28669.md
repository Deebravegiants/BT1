# [H] mm/secretmem: fix GUP-fast succeeding on secretmem folios

## Summary
Severity: High
Advisory: CVE-2024-35872
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35872
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/secretmem: fix GUP-fast succeeding on secretmem folios

folio_is_secretmem() currently relies on secretmem folios being LRU
folios, to save some cycles.

However, folios might reside in a folio batch without the LRU flag set, or
temporarily have their LRU flag cleared.  Consequently, the LRU flag is
unreliable for this purpose.

In particular, this is the case when secretmem_fault() allocates a fresh
page and calls filemap_add_folio()->folio_add_lru().  The folio might be
added to the per-cpu folio batch and won't get the LRU flag set until the
batch was drained using e.g., lru_add_drain().

Consequently, folio_is_secretmem() might not detect secretmem folios and
GUP-fast can succeed in grabbing a secretmem folio, crashing the kernel
when we would later try reading/writing to the folio, because the folio
has been unmapped from the directmap.

Fix it by removing that unreliable check.

## References
- https://git.kernel.org/stable/c/201e4aaf405dfd1308da54448654053004c579b5
- https://git.kernel.org/stable/c/43fad1d0284de30159661d0badfc3cbaf7e6f8f8
- https://git.kernel.org/stable/c/65291dcfcf8936e1b23cfd7718fdfde7cfaf7706
- https://git.kernel.org/stable/c/6564b014af92b677c1f07c44d7f5b595d589cf6e
- https://git.kernel.org/stable/c/9c2b4b657739ecda38e3b383354a29566955ac48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35872.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
