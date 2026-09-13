# [H] ceph: put folios not suitable for writeback

## Summary
Severity: High
Advisory: CVE-2026-52960
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52960
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: put folios not suitable for writeback

The batch holds references to the folios (see `filemap_get_folios`,
`folio_batch_release`), so we need to `folio_put` the folios we remove.

Tested on v6.18.

## References
- https://git.kernel.org/stable/c/544576f0f05c4a759806acddfaaeb686f14fb4b0
- https://git.kernel.org/stable/c/86921e890fe1dea9791fb70bec552516fd47716a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52960.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52960
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
