# [H] mm/percpu-km: fix bitmap overflow and accounting in pcpu_create_chunk()

## Summary
Severity: High
Advisory: CVE-2026-80718
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80718
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/percpu-km: fix bitmap overflow and accounting in pcpu_create_chunk()

In pcpu_create_chunk(), nr_pages is the total contiguous backing
allocation, i.e., nr_units * pcpu_unit_pages, but pcpu_chunk_populated()
uses it to set chunk->populated, whose size is pcpu_unit_pages, bitmap. 
Since bit N in chunk->populated means page offset N inside every unit is
backed.  When nr_units > 1, the function writes beyond chunk->populated. 
Fix it by using chunk->nr_pages.

It also fixes the global pcpu_nr_empty_pop_pages accounting, since
pcpu_balance_free() only iterates up to chunk->nr_pages.

Commit a63d4ac4ab609 ("percpu: make percpu-km set chunk->populated bitmap
properly") introduced the bitmap overflow issue.  Later, commit
b539b87fed37f ("percpu: implmeent pcpu_nr_empty_pop_pages and
chunk->nr_populated") added pcpu_nr_empty_pop_pages and caused the
accounting issue.

## References
- https://git.kernel.org/stable/c/01504da375f5b19df195cb1cb1cf1dd184318f97
- https://git.kernel.org/stable/c/32134cf9211b83bed9076d0739c5906fbea4c763
- https://git.kernel.org/stable/c/5c7fc39bf19abb38a996aaad77b3e3a8f48581c3
- https://git.kernel.org/stable/c/5f43d2c1bea280dcdfabaf156c25e7402fb8039f
- https://git.kernel.org/stable/c/6fc7da2a052f2825fff785e860e67183f5acaaba
- https://git.kernel.org/stable/c/89b1b79c308818a715e75f28744b70d8940a07c9
- https://git.kernel.org/stable/c/92c43ac3c2b09eb16162e8144e73c00b7c3e29d6
- https://git.kernel.org/stable/c/a6940b84c8c035da465b7165fdfcfb005545724e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80718.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
