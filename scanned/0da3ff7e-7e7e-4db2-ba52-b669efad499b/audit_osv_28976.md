# [M] ASoC: kirkwood: Fix potential NULL dereference

## Summary
Severity: Medium
Advisory: CVE-2024-38550
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38550
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: kirkwood: Fix potential NULL dereference

In kirkwood_dma_hw_params() mv_mbus_dram_info() returns NULL if
CONFIG_PLAT_ORION macro is not defined.
Fix this bug by adding NULL check.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/1a7254525ca7a6f3e37d7882d7f7ad97f6235f7c
- https://git.kernel.org/stable/c/5bf5154739cd676b6d0958079070557c8d96afb6
- https://git.kernel.org/stable/c/802b49e39da669b54bd9b77dc3c649999a446bf6
- https://git.kernel.org/stable/c/d48d0c5fd733bd6d8d3ddb2ed553777ab4724169
- https://git.kernel.org/stable/c/de9987cec6fde1dd41dfcb971433e05945852489
- https://git.kernel.org/stable/c/ea60ab95723f5738e7737b56dda95e6feefa5b50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38550.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38550
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
