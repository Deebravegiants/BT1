# [H] CVE-2017-10810

## Summary
Severity: High
Advisory: CVE-2017-10810
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-04
Source: https://osv.dev/vulnerability/CVE-2017-10810
Type: osv

## Details
Memory leak in the virtio_gpu_object_create function in drivers/gpu/drm/virtio/virtgpu_object.c in the Linux kernel through 4.11.8 allows attackers to cause a denial of service (memory consumption) by triggering object-initialization failures.

## References
- http://www.debian.org/security/2017/dsa-3927
- http://www.securityfocus.com/bid/99433
- https://github.com/torvalds/linux/commit/385aee965b4e4c36551c362a334378d2985b722a
- https://lkml.org/lkml/2017/4/6/668
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=385aee965b4e4c36551c362a334378d2985b722a
