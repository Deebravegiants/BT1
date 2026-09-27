# [H] drm/amd/display: Do not skip unrelated mode changes in DSC validation

## Summary
Severity: High
Advisory: CVE-2026-31488
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31488
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Do not skip unrelated mode changes in DSC validation

Starting with commit 17ce8a6907f7 ("drm/amd/display: Add dsc pre-validation in
atomic check"), amdgpu resets the CRTC state mode_changed flag to false when
recomputing the DSC configuration results in no timing change for a particular
stream.

However, this is incorrect in scenarios where a change in MST/DSC configuration
happens in the same KMS commit as another (unrelated) mode change. For example,
the integrated panel of a laptop may be configured differently (e.g., HDR
enabled/disabled) depending on whether external screens are attached. In this
case, plugging in external DP-MST screens may result in the mode_changed flag
being dropped incorrectly for the integrated panel if its DSC configuration
did not change during precomputation in pre_validate_dsc().

At this point, however, dm_update_crtc_state() has already created new streams
for CRTCs with DSC-independent mode changes. In turn,
amdgpu_dm_commit_streams() will never release the old stream, resulting in a
memory leak. amdgpu_dm_atomic_commit_tail() will never acquire a reference to
the new stream either, which manifests as a use-after-free when the stream gets
disabled later on:

BUG: KASAN: use-after-free in dc_stream_release+0x25/0x90 [amdgpu]
Write of size 4 at addr ffff88813d836524 by task kworker/9:9/29977

Workqueue: events drm_mode_rmfb_work_fn
Call Trace:
 <TASK>
 dump_stack_lvl+0x6e/0xa0
 print_address_description.constprop.0+0x88/0x320
 ? dc_stream_release+0x25/0x90 [amdgpu]
 print_report+0xfc/0x1ff
 ? srso_alias_return_thunk+0x5/0xfbef5
 ? __virt_addr_valid+0x225/0x4e0
 ? dc_stream_release+0x25/0x90 [amdgpu]
 kasan_report+0xe1/0x180
 ? dc_stream_release+0x25/0x90 [amdgpu]
 kasan_check_range+0x125/0x200
 dc_stream_release+0x25/0x90 [amdgpu]
 dc_state_destruct+0x14d/0x5c0 [amdgpu]
 dc_state_release.part.0+0x4e/0x130 [amdgpu]
 dm_atomic_destroy_state+0x3f/0x70 [amdgpu]
 drm_atomic_state_default_clear+0x8ee/0xf30
 ? drm_mode_object_put.part.0+0xb1/0x130
 __drm_atomic_state_free+0x15c/0x2d0
 atomic_remove_fb+0x67e/0x980

Since there is no reliable way of figuring out whether a CRTC has unrelated
mode changes pending at the time of DSC validation, remember the value of the
mode_changed flag from before the point where a CRTC was marked as potentially
affected by a change in DSC configuration. Reset the mode_changed flag to this
earlier value instead in pre_validate_dsc().

(cherry picked from commit cc7c7121ae082b7b82891baa7280f1ff2608f22b)

## References
- https://git.kernel.org/stable/c/10862e344b4d6434642a48c87d765813fc0b0ba7
- https://git.kernel.org/stable/c/111208b5b7ebcdadb3f922cc52d8425f0fa91b33
- https://git.kernel.org/stable/c/21159d8b335a6b9f44cbb506733013a902ae2da4
- https://git.kernel.org/stable/c/8a5edc97fd9c6415ff2eff872748439a97e3c3d8
- https://git.kernel.org/stable/c/aed3d041ab061ec8a64f50a3edda0f4db7280025
- https://git.kernel.org/stable/c/da1d0ed31e9802fd99384f43cc63678a5a11cb41
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31488.json
- https://access.redhat.com/errata/RHSA-2026:27353
- https://access.redhat.com/errata/RHSA-2026:27354
- https://access.redhat.com/errata/RHSA-2026:30848
- https://access.redhat.com/errata/RHSA-2026:43231
- https://access.redhat.com/errata/RHSA-2026:44385
- https://access.redhat.com/errata/RHSA-2026:47632
- https://access.redhat.com/errata/RHSA-2026:47739
- https://access.redhat.com/errata/RHSA-2026:47869
- https://access.redhat.com/errata/RHSA-2026:53330
- https://access.redhat.com/errata/RHSA-2026:55445
- https://access.redhat.com/security/cve/CVE-2026-31488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31488.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31488
