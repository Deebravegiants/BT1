# [H] ASoC: hdmi-codec: Fix OOB memory accesses

## Summary
Severity: High
Advisory: CVE-2022-48739
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48739
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: hdmi-codec: Fix OOB memory accesses

Correct size of iec_status array by changing it to the size of status
array of the struct snd_aes_iec958. This fixes out-of-bounds slab
read accesses made by memcpy() of the hdmi-codec driver. This problem
is reported by KASAN.

## References
- https://git.kernel.org/stable/c/06feec6005c9d9500cd286ec440aabf8b2ddd94d
- https://git.kernel.org/stable/c/10007bd96b6c4c3cfaea9e76c311b06a07a5e260
- https://git.kernel.org/stable/c/1552e66be325a21d7eff49f46013fb402165a0ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48739.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
