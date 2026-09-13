# [H] ntfs: serialize volume label accesses

## Summary
Severity: High
Advisory: CVE-2026-63793
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63793
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: serialize volume label accesses

Protect vol->volume_label with a mutex and snaphost the label before
copy_to_user. This prevent a use-after-free when FS_IOC_SETFSLABEL
replaces the vol->volume_label and FS_IOC_GETTSLABEL reads it
concurrently.

## References
- https://git.kernel.org/stable/c/acd744019460bad22e43d4569a502f9c88d331ae
- https://git.kernel.org/stable/c/e9e50ce4f13dc721014af622613409455c734942
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63793.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63793
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
