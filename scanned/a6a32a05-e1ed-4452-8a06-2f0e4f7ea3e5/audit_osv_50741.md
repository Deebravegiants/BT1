# [M] CVE-2020-36775

## Summary
Severity: Medium
Advisory: CVE-2020-36775
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2020-36775
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid potential deadlock

Using f2fs_trylock_op() in f2fs_write_compressed_pages() to avoid potential
deadlock like we did in f2fs_write_single_data_page().

## References
- https://git.kernel.org/stable/c/0478ccdc8ea016de1ebaf6fe6da0275c2b258c5b
- https://git.kernel.org/stable/c/8e8542437bb4070423c9754d5ba270ffdbae8c8d
- https://git.kernel.org/stable/c/df77fbd8c5b222c680444801ffd20e8bbc90a56e
