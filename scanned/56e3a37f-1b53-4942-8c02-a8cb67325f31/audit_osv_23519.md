# [H] scsi: target: tcmu: Fix possible page UAF

## Summary
Severity: High
Advisory: CVE-2022-49053
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49053
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.276, >=4.15.0 <4.19.239, >=4.20.0 <5.4.190, >=5.5.0 <5.10.112, >=5.11.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: tcmu: Fix possible page UAF

tcmu_try_get_data_page() looks up pages under cmdr_lock, but it does not
take refcount properly and just returns page pointer. When
tcmu_try_get_data_page() returns, the returned page may have been freed by
tcmu_blocks_release().

We need to get_page() under cmdr_lock to avoid concurrent
tcmu_blocks_release().

## References
- https://git.kernel.org/stable/c/a6968f7a367f128d120447360734344d5a3d5336
- https://git.kernel.org/stable/c/a9564d84ed9f6ee71017d062d0d2182154294a4b
- https://git.kernel.org/stable/c/aec36b98a1bbaa84bfd8299a306e4c12314af626
- https://git.kernel.org/stable/c/b7f3b5d70c834f49f7d87a2f2ed1c6284d9a0322
- https://git.kernel.org/stable/c/d7c5d79e50be6e06b669141e3db1f977a0dd4e8e
- https://git.kernel.org/stable/c/e3e0e067d5b34e4a68e3cc55f8eebc413f56f8ed
- https://git.kernel.org/stable/c/fb7a5115422fbd6a4d505e8844f1ef5529f10489
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49053.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
