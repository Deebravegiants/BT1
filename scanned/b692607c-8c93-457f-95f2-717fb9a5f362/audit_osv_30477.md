# [M] drm/mediatek: Fix potential NULL dereference in mtk_crtc_destroy()

## Summary
Severity: Medium
Advisory: CVE-2024-53056
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53056
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: Fix potential NULL dereference in mtk_crtc_destroy()

In mtk_crtc_create(), if the call to mbox_request_channel() fails then we
set the "mtk_crtc->cmdq_client.chan" pointer to NULL.  In that situation,
we do not call cmdq_pkt_create().

During the cleanup, we need to check if the "mtk_crtc->cmdq_client.chan"
is NULL first before calling cmdq_pkt_destroy().  Calling
cmdq_pkt_destroy() is unnecessary if we didn't call cmdq_pkt_create() and
it will result in a NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/4018651ba5c409034149f297d3dd3328b91561fd
- https://git.kernel.org/stable/c/c60583a87cb4a85b69d1f448f0be5eb6ec62cbb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53056.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53056
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
