# [H] drm/gem: Acquire references on GEM handles for framebuffers

## Summary
Severity: High
Advisory: CVE-2025-38449
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38449
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/gem: Acquire references on GEM handles for framebuffers

A GEM handle can be released while the GEM buffer object is attached
to a DRM framebuffer. This leads to the release of the dma-buf backing
the buffer object, if any. [1] Trying to use the framebuffer in further
mode-setting operations leads to a segmentation fault. Most easily
happens with driver that use shadow planes for vmap-ing the dma-buf
during a page flip. An example is shown below.

[  156.791968] ------------[ cut here ]------------
[  156.796830] WARNING: CPU: 2 PID: 2255 at drivers/dma-buf/dma-buf.c:1527 dma_buf_vmap+0x224/0x430
[...]
[  156.942028] RIP: 0010:dma_buf_vmap+0x224/0x430
[  157.043420] Call Trace:
[  157.045898]  <TASK>
[  157.048030]  ? show_trace_log_lvl+0x1af/0x2c0
[  157.052436]  ? show_trace_log_lvl+0x1af/0x2c0
[  157.056836]  ? show_trace_log_lvl+0x1af/0x2c0
[  157.061253]  ? drm_gem_shmem_vmap+0x74/0x710
[  157.065567]  ? dma_buf_vmap+0x224/0x430
[  157.069446]  ? __warn.cold+0x58/0xe4
[  157.073061]  ? dma_buf_vmap+0x224/0x430
[  157.077111]  ? report_bug+0x1dd/0x390
[  157.080842]  ? handle_bug+0x5e/0xa0
[  157.084389]  ? exc_invalid_op+0x14/0x50
[  157.088291]  ? asm_exc_invalid_op+0x16/0x20
[  157.092548]  ? dma_buf_vmap+0x224/0x430
[  157.096663]  ? dma_resv_get_singleton+0x6d/0x230
[  157.101341]  ? __pfx_dma_buf_vmap+0x10/0x10
[  157.105588]  ? __pfx_dma_resv_get_singleton+0x10/0x10
[  157.110697]  drm_gem_shmem_vmap+0x74/0x710
[  157.114866]  drm_gem_vmap+0xa9/0x1b0
[  157.118763]  drm_gem_vmap_unlocked+0x46/0xa0
[  157.123086]  drm_gem_fb_vmap+0xab/0x300
[  157.126979]  drm_atomic_helper_prepare_planes.part.0+0x487/0xb10
[  157.133032]  ? lockdep_init_map_type+0x19d/0x880
[  157.137701]  drm_atomic_helper_commit+0x13d/0x2e0
[  157.142671]  ? drm_atomic_nonblocking_commit+0xa0/0x180
[  157.147988]  drm_mode_atomic_ioctl+0x766/0xe40
[...]
[  157.346424] ---[ end trace 0000000000000000 ]---

Acquiring GEM handles for the framebuffer's GEM buffer objects prevents
this from happening. The framebuffer's cleanup later puts the handle
references.

Commit 1a148af06000 ("drm/gem-shmem: Use dma_buf from GEM object
instance") triggers the segmentation fault easily by using the dma-buf
field more widely. The underlying issue with reference counting has
been present before.

v2:
- acquire the handle instead of the BO (Christian)
- fix comment style (Christian)
- drop the Fixes tag (Christian)
- rename err_ gotos
- add missing Link tag

## References
- https://git.kernel.org/stable/c/08480e285c6a82ce689008d643e4a51db0aaef8b
- https://git.kernel.org/stable/c/3cf520d9860d4ec9f7f32068825da31f18dd3f25
- https://git.kernel.org/stable/c/5307dce878d4126e1b375587318955bd019c3741
- https://git.kernel.org/stable/c/cb4c956a15f8b7f870649454771fc3761f504b5f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38449.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38449
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
