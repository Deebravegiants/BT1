# [H] exfat: fix the new buffer was not zeroed before writing

## Summary
Severity: High
Advisory: CVE-2024-57943
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57943
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: fix the new buffer was not zeroed before writing

Before writing, if a buffer_head marked as new, its data must
be zeroed, otherwise uninitialized data in the page cache will
be written.

So this commit uses folio_zero_new_buffers() to zero the new
buffers before ->write_end().

## References
- https://git.kernel.org/stable/c/942c6f91ab8d82a41650e717940b4e577173762f
- https://git.kernel.org/stable/c/98e2fb26d1a9eafe79f46d15d54e68e014d81d8c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57943.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57943
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
