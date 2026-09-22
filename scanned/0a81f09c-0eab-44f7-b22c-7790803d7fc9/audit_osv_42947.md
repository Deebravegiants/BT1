# [H] ntfs: centalize $INDEX_ROOT header validation

## Summary
Severity: High
Advisory: CVE-2026-72204
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72204
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: centalize $INDEX_ROOT header validation

Add a dedicated helper to perform stricter validation of $INDEX_ROOT and
use it for both directory inodes and named index inodes. This keeps the
root size and header geometry checks consistent across both read paths.

## References
- https://git.kernel.org/stable/c/8b97b302f553a480fb76d2afd53cd6c0635a9dcd
- https://git.kernel.org/stable/c/b06730c6af58d3569883f8dd7c36a90aba5ecc0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72204.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72204
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
