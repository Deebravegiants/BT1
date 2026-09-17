# [C] mm: call ->free_folio() directly in folio_unmap_invalidate()

## Summary
Severity: Critical
Advisory: CVE-2026-31589
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31589
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.27, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: call ->free_folio() directly in folio_unmap_invalidate()

We can only call filemap_free_folio() if we have a reference to (or hold a
lock on) the mapping.  Otherwise, we've already removed the folio from the
mapping so it no longer pins the mapping and the mapping can be removed,
causing a use-after-free when accessing mapping->a_ops.

Follow the same pattern as __remove_mapping() and load the free_folio
function pointer before dropping the lock on the mapping.  That lets us
make filemap_free_folio() static as this was the only caller outside
filemap.c.

## References
- https://git.kernel.org/stable/c/615d9bb2ccad42f9e21d837431e401db2e471195
- https://git.kernel.org/stable/c/b667df39d98a7a24be7c2a40ff0863dac1ad2cd7
- https://git.kernel.org/stable/c/c330e65ea59c4805d6ab6757c4ddfe8c63acef31
- https://git.kernel.org/stable/c/efc52947247a21bbf79059539bbbd40f4ea76f00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31589.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31589
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
