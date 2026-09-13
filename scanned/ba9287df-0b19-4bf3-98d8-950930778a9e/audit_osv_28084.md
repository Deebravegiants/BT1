# [H] drm/nouveau: keep DMA buffers required for suspend/resume

## Summary
Severity: High
Advisory: CVE-2024-27411
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27411
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.6 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/nouveau: keep DMA buffers required for suspend/resume

Nouveau deallocates a few buffers post GPU init which are required for GPU suspend/resume to function correctly.
This is likely not as big an issue on systems where the NVGPU is the only GPU, but on multi-GPU set ups it leads to a regression where the kernel module errors and results in a system-wide rendering freeze.

This commit addresses that regression by moving the two buffers required for suspend and resume to be deallocated at driver unload instead of post init.

## References
- https://git.kernel.org/stable/c/be00e15b240ed71fc30c0576af7ab670c8271661
- https://git.kernel.org/stable/c/f6ecfdad359a01c7fd8a3bcfde3ef0acdf107e6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27411.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
