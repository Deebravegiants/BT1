# [M] CVE-2023-22998

## Summary
Severity: Medium
Advisory: CVE-2023-22998
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-22998
Type: osv

## Details
In the Linux kernel before 6.0.3, drivers/gpu/drm/virtio/virtgpu_object.c misinterprets the drm_gem_shmem_get_sg_table return value (expects it to be NULL in the error case, whereas it is actually an error pointer).

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.3
- https://github.com/torvalds/linux/commit/c24968734abfed81c8f93dc5f44a7b7a9aecadfa
