# [H] hpfs: fix a crash if hpfs_map_dnode_bitmap fails

## Summary
Severity: High
Advisory: CVE-2026-63954
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63954
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

hpfs: fix a crash if hpfs_map_dnode_bitmap fails

If hpfs_map_dnode_bitmap fails, the code would call hpfs_brelse4 on
uninitialized quad buffer head, causing a crash.

## References
- https://git.kernel.org/stable/c/010b08084000ef018f1a8de5197087f3b91d8cfe
- https://git.kernel.org/stable/c/0886c6f257fe3663f80218aa1919b0f3f21bf22c
- https://git.kernel.org/stable/c/1648a3c7f4e18f46a4881920133fc4f2494185a0
- https://git.kernel.org/stable/c/1d73a533760bc5abb83b3cc759133596f7bb708f
- https://git.kernel.org/stable/c/4f37bb30b57d6d403d02673074555bd3c3602bef
- https://git.kernel.org/stable/c/7c58c55a2a16f7274772507bd1637be609351b4f
- https://git.kernel.org/stable/c/974820a59efde7c1a7e1260bcfe9bb81f833cc9f
- https://git.kernel.org/stable/c/d98d8562b3284b5a5c8eb67e71b794508e46e288
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63954.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
