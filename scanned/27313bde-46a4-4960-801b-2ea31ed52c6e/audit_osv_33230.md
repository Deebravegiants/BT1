# [H] erofs: fix invalid algorithm for encoded extents

## Summary
Severity: High
Advisory: CVE-2025-39924
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39924
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix invalid algorithm for encoded extents

The current algorithm sanity checks do not properly apply to new
encoded extents.

Unify the algorithm check with Z_EROFS_COMPRESSION(_RUNTIME)_MAX
and ensure consistency with sbi->available_compr_algs.

## References
- https://git.kernel.org/stable/c/131897c65e2b86cf14bec7379f44aa8fbb407526
- https://git.kernel.org/stable/c/db5d7abd379a8dcf030be8f52f99cadf7e397ba8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39924.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
