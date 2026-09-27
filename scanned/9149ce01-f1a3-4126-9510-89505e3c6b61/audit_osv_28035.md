# [H] f2fs: compress: fix to cover normal cluster write with cp_rwsem

## Summary
Severity: High
Advisory: CVE-2024-27034
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27034
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: fix to cover normal cluster write with cp_rwsem

When we overwrite compressed cluster w/ normal cluster, we should
not unlock cp_rwsem during f2fs_write_raw_pages(), otherwise data
will be corrupted if partial blocks were persisted before CP & SPOR,
due to cluster metadata wasn't updated atomically.

## References
- https://git.kernel.org/stable/c/2b1b14d9fc94b8feae20808684c8af28ec80f45b
- https://git.kernel.org/stable/c/52982edfcefd475cc34af663d5c47c0cddaa5739
- https://git.kernel.org/stable/c/542c8b3c774a480bfd0804291a12f6f2391b0cd1
- https://git.kernel.org/stable/c/75abfd61392b1db391bde6d738a30d685b843286
- https://git.kernel.org/stable/c/7d420eaaa18ec8e2bb4eeab8c65c00492ef6f416
- https://git.kernel.org/stable/c/fd244524c2cf07b5f4c3fe8abd6a99225c76544b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27034.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27034
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
