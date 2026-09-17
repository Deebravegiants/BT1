# [H] ext4: fix possible double unlock when moving a directory

## Summary
Severity: High
Advisory: CVE-2023-53626
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53626
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.237 <5.4.238, >=5.10.175 <5.10.176, >=5.15.103 <5.15.104, >=6.1.20 <6.1.21, >=6.2.7 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix possible double unlock when moving a directory

## References
- https://git.kernel.org/stable/c/020166bc6669ca9fb267ebd96bd88c4fb64a5d46
- https://git.kernel.org/stable/c/1c93c42c7bb23057bde8a0a2ab834927ff64d20c
- https://git.kernel.org/stable/c/43ce288ab5d7274a4a141d7f5e3ed2ab7b41f8a2
- https://git.kernel.org/stable/c/70e42feab2e20618ddd0cbfc4ab4b08628236ecd
- https://git.kernel.org/stable/c/c16cbd8233d6c58fc488545393e49b5d55729990
- https://git.kernel.org/stable/c/e71eb4dca41f0f36823724ced0406bb2dbdd5506
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53626.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53626
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
