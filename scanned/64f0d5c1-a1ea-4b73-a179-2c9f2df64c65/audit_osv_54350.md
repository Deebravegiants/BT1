# [H] CVE-2023-51042

## Summary
Severity: High
Advisory: CVE-2023-51042
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2023-51042
Type: osv

## Details
In the Linux kernel before 6.4.12, amdgpu_cs_wait_all_fences in drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c has a fence use-after-free.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.12
- https://github.com/torvalds/linux/commit/2e54154b9f27262efd0cb4f903cc7d5ad1fe9628
