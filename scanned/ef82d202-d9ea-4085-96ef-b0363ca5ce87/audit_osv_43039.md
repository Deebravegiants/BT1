# [H] netfs: Fix writeback error handling

## Summary
Severity: High
Advisory: CVE-2026-72364
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72364
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix writeback error handling

Fix the error handling in writeback_iter() loop.  If an error occurs,
writeback_iter() needs to be called again with *error set to the error so
that it can clean up iteration state.  Further, the current folio needs
unlocking and redirtying.

## References
- https://git.kernel.org/stable/c/1bb33d959aabcde07d724b5eb9992462e91fa79a
- https://git.kernel.org/stable/c/89df9c158a25d0a7c6ca079a9bd9ca7009d75c7b
- https://git.kernel.org/stable/c/ac5f95ac5d6d0f4c567b8b642825705a2bf0d79e
- https://git.kernel.org/stable/c/fb39ffd3cc5422887fd118668ff45ebfdbc83302
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72364.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
