# [H] drm/amdkfd: Fix watch_id bounds checking in debug address watch v2

## Summary
Severity: High
Advisory: CVE-2026-45878
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45878
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix watch_id bounds checking in debug address watch v2

The address watch clear code receives watch_id as an unsigned value
(u32), but some helper functions were using a signed int and checked
bits by shifting with watch_id.

If a very large watch_id is passed from userspace, it can be converted
to a negative value.  This can cause invalid shifts and may access
memory outside the watch_points array.

drm/amdkfd: Fix watch_id bounds checking in debug address watch v2

Fix this by checking that watch_id is within MAX_WATCH_ADDRESSES before
using it.  Also use BIT(watch_id) to test and clear bits safely.

This keeps the behavior unchanged for valid watch IDs and avoids
undefined behavior for invalid ones.

Fixes the below:
drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_debug.c:448
kfd_dbg_trap_clear_dev_address_watch() error: buffer overflow
'pdd->watch_points' 4 <= u32max user_rl='0-3,2147483648-u32max' uncapped

drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_debug.c
    433 int kfd_dbg_trap_clear_dev_address_watch(struct kfd_process_device *pdd,
    434                                         uint32_t watch_id)
    435 {
    436         int r;
    437
    438         if (!kfd_dbg_owns_dev_watch_id(pdd, watch_id))

kfd_dbg_owns_dev_watch_id() doesn't check for negative values so if
watch_id is larger than INT_MAX it leads to a buffer overflow.
(Negative shifts are undefined).

    439                 return -EINVAL;
    440
    441         if (!pdd->dev->kfd->shared_resources.enable_mes) {
    442                 r = debug_lock_and_unmap(pdd->dev->dqm);
    443                 if (r)
    444                         return r;
    445         }
    446
    447         amdgpu_gfx_off_ctrl(pdd->dev->adev, false);
--> 448         pdd->watch_points[watch_id] = pdd->dev->kfd2kgd->clear_address_watch(
    449                                                         pdd->dev->adev,
    450                                                         watch_id);

v2: (as per, Jonathan Kim)
 - Add early watch_id >= MAX_WATCH_ADDRESSES validation in the set path to
   match the clear path.
 - Drop the redundant bounds check in kfd_dbg_owns_dev_watch_id().

## References
- https://git.kernel.org/stable/c/2b36c0c1bcbbe15f6cfa9652084b3124c835a150
- https://git.kernel.org/stable/c/3c38a0f07aa2bfef2b219b1f045534ad93f85afd
- https://git.kernel.org/stable/c/5a19302cab5cec7ae7f1a60c619951e6c17d8742
- https://git.kernel.org/stable/c/971bf8e61e9b4abaacf9b35eaf76ec222758f9d6
- https://git.kernel.org/stable/c/a0d367e13db63a6ed76ee0d0a8c3a58c1fa98488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45878.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45878
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
