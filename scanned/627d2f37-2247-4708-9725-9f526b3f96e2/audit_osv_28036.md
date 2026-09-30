# [H] f2fs: compress: fix to guarantee persisting compressed blocks by CP

## Summary
Severity: High
Advisory: CVE-2024-27035
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27035
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: fix to guarantee persisting compressed blocks by CP

If data block in compressed cluster is not persisted with metadata
during checkpoint, after SPOR, the data may be corrupted, let's
guarantee to write compressed page by checkpoint.

## References
- https://git.kernel.org/stable/c/57e8b17d0522c8f4daf0c4d9969b4d7358033532
- https://git.kernel.org/stable/c/82704e598d7b33c7e45526e34d3c585426319bed
- https://git.kernel.org/stable/c/8a430dd49e9cb021372b0ad91e60aeef9c6ced00
- https://git.kernel.org/stable/c/c3311694b9bcced233548574d414c91d39214684
- https://git.kernel.org/stable/c/e54cce8137258a550b49cae45d09e024821fb28d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27035.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27035
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
