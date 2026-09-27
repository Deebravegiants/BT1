# [H] drm/i915: clear CRTC color blob pointers after dropping refs

## Summary
Severity: High
Advisory: CVE-2026-72452
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72452
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: clear CRTC color blob pointers after dropping refs

intel_crtc_put_color_blobs() drops the CRTC color blob references, but
leaves the corresponding pointers unchanged.

This can matter in intel_crtc_prepare_cleared_state(), which frees the
old CRTC hw state before calling intel_dp_tunnel_atomic_clear_stream_bw().
The latter can fail while looking up the DP tunnel group state, for
example with -EDEADLK.

If that happens, the function returns without completing the cleared
state preparation. The failed atomic state will then be cleared by the
atomic core and intel_crtc_free_hw_state() can be called again for the
same state, dropping the same blob references again.

Clear the blob pointers after dropping the references so repeated cleanup
of the same CRTC hw state is safe.

(cherry picked from commit d5005addb5f68e8a0edce249506757bdc9e3d8c8)

## References
- https://git.kernel.org/stable/c/164afa1a3af8e8c91b4a6d5fd7b79a44ec70abf0
- https://git.kernel.org/stable/c/2024940522ef451098c940ab0b82d647de5e5d9b
- https://git.kernel.org/stable/c/31f077088e0faae6be8377741f356dea1b94ba46
- https://git.kernel.org/stable/c/ac554ad943610031a25795d6ef71316f6164c136
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72452
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
