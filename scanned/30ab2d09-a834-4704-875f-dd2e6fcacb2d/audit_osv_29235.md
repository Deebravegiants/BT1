# [H] drm/amdgpu: Fix signedness bug in sdma_v4_0_process_trap_irq()

## Summary
Severity: High
Advisory: CVE-2024-41022
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41022
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.102, >=6.2.0 <6.6.43, >=6.7.0 <6.9.12, >=6.10.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix signedness bug in sdma_v4_0_process_trap_irq()

The "instance" variable needs to be signed for the error handling to work.

## References
- https://git.kernel.org/stable/c/298e2ce222e712ffafa47288c5b2fcf33d72fda3
- https://git.kernel.org/stable/c/3dd9734878a9042f0358301d19a2b006a0fc4d06
- https://git.kernel.org/stable/c/4edb0a84e6b32e75dc9bd6dd085b2c2ff19ec287
- https://git.kernel.org/stable/c/544fa213f15d27f0370795845d55eeb3e00080d2
- https://git.kernel.org/stable/c/6769a23697f17f9bf9365ca8ed62fe37e361a05a
- https://git.kernel.org/stable/c/a5224e2123ce21102f346f518db80f004d5053a7
- https://git.kernel.org/stable/c/d347c9a398bf7eab9408d207c0a50fb720f9de7d
- https://git.kernel.org/stable/c/e8dfbf83a82bbfb9680921719fbe65e535af59ea
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41022.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
