# [H] drm/amd/display: set new_stream to NULL after release

## Summary
Severity: High
Advisory: CVE-2026-68236
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68236
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: set new_stream to NULL after release

In dm_update_crtc_state(), the skip_modeset path releases new_stream
via dc_stream_release() but does not set the pointer to NULL.

If a later error (e.g., color management failure) triggers the fail
label, the error path calls dc_stream_release() again on the same
dangling pointer, causing a double release and potential use-after-free.

Fix this by setting new_stream to NULL after the initial release.

(cherry picked from commit 99f3af19073b3ddbfd96e789124cce12c4277b28)

## References
- https://git.kernel.org/stable/c/0676fecbb5242aa22c057e78326d6d6041db034c
- https://git.kernel.org/stable/c/5182e442e61397d446c36995b8f5676942d35b82
- https://git.kernel.org/stable/c/679f23f0a3606afcef1ffabd72222f00a54ad9e3
- https://git.kernel.org/stable/c/9fa26b9eed6195bf840f39ac183b9a6237548755
- https://git.kernel.org/stable/c/ba8bf1dcbb44773e7a0fd13b42925c644e0d5e76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68236.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
