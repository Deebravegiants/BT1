# [H] mm/zone_device: do not touch device folio after calling ->folio_free()

## Summary
Severity: High
Advisory: CVE-2026-46277
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46277
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/zone_device: do not touch device folio after calling ->folio_free()

The contents of a device folio can immediately change after calling
->folio_free(), as the folio may be reallocated by a driver with a
different order.  Instead of touching the folio again to extract the
pgmap, use the local stack variable when calling percpu_ref_put_many().

## References
- https://git.kernel.org/stable/c/39928984956037cabd304321cb8f342e47421db5
- https://git.kernel.org/stable/c/85be0a262e39c706edb53c88af8afde2e98222ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46277.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
