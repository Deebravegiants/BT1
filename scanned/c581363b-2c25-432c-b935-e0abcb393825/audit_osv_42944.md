# [C] ntfs: validate index entries on reading

## Summary
Severity: Critical
Advisory: CVE-2026-72201
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72201
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: validate index entries on reading

Validate index entries immediately after reading an index root or index
block from disk. This eliminates repeated checks in lookup and readdir,
and reduce the risk of missing checks in those paths.

## References
- https://git.kernel.org/stable/c/2221b691d7b2e17f08153f95848dacaa5d87e21d
- https://git.kernel.org/stable/c/e2b95d3adb558ddd5685f9e072ec8661d57ee3a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72201.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
