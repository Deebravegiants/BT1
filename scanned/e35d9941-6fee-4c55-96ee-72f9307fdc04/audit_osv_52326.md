# [M] CVE-2021-47332

## Summary
Severity: Medium
Advisory: CVE-2021-47332
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47332
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usx2y: Don't call free_pages_exact() with NULL address

Unlike some other functions, we can't pass NULL pointer to
free_pages_exact().  Add a proper NULL check for avoiding possible
Oops.

## References
- https://git.kernel.org/stable/c/7d7f30cf182e55023fa8fde4c084b2d37c6be69d
- https://git.kernel.org/stable/c/82e5ee742fdd8874fe996181b87fafe1eb5f1196
- https://git.kernel.org/stable/c/88262229b778f4f7a896da828d966f94dcb35d19
- https://git.kernel.org/stable/c/bee295f5e03510252d18b25cc1d26230256eb87a
- https://git.kernel.org/stable/c/cae0cf651adccee2c3f376e78f30fbd788d0829f
