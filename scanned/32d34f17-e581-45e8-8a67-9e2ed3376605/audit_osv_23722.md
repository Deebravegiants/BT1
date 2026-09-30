# [H] ubi: ubi_create_volume: Fix use-after-free when volume creation failed

## Summary
Severity: High
Advisory: CVE-2022-49388
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49388
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubi: ubi_create_volume: Fix use-after-free when volume creation failed

There is an use-after-free problem for 'eba_tbl' in ubi_create_volume()'s
error handling path:

  ubi_eba_replace_table(vol, eba_tbl)
    vol->eba_tbl = tbl
out_mapping:
  ubi_eba_destroy_table(eba_tbl)   // Free 'eba_tbl'
out_unlock:
  put_device(&vol->dev)
    vol_release
      kfree(tbl->entries)	  // UAF

Fix it by removing redundant 'eba_tbl' releasing.
Fetch a reproducer in [Link].

## References
- https://git.kernel.org/stable/c/1174ab8ba36a48025b68b5ff1085000b1e510217
- https://git.kernel.org/stable/c/25ff1e3a1351c0d936dd1ac2f9e58231ea1510c9
- https://git.kernel.org/stable/c/5ff2514e4fb55dcf3d88294686040ca73ea0c1a2
- https://git.kernel.org/stable/c/6d8d3f68cbecfd31925796f0fb668eb21ab06734
- https://git.kernel.org/stable/c/8302620aeb940f386817321d272b12411ae7d39f
- https://git.kernel.org/stable/c/8c03a1c21d72210f81cb369cc528e3fde4b45411
- https://git.kernel.org/stable/c/abb67043060f2bf4c03d7c3debb9ae980e2b6db3
- https://git.kernel.org/stable/c/e27ecf325e51abd06aaefba57a6322a46fa4178b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49388.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
