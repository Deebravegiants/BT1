# [C] ntfs: add bounds check before accessing EA entries

## Summary
Severity: Critical
Advisory: CVE-2026-72208
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72208
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: add bounds check before accessing EA entries

in ntfs_ea_lookup and ntfs_listxattr, this verifies that there is enough
space in the EA entry before accessing the next_entry_offset field of
the EA entry.

## References
- https://git.kernel.org/stable/c/937282f7d15b593d0be765fa2ced164130ec87f7
- https://git.kernel.org/stable/c/d9d9925de1d8f233cc60d3dc356e12f232f97c15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
