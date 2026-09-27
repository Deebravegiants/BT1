# [M] CVE-2021-47108

## Summary
Severity: Medium
Advisory: CVE-2021-47108
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47108
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: hdmi: Perform NULL pointer check for mtk_hdmi_conf

In commit 41ca9caaae0b
("drm/mediatek: hdmi: Add check for CEA modes only") a check
for CEA modes was added to function mtk_hdmi_bridge_mode_valid()
in order to address possible issues on MT8167;
moreover, with commit c91026a938c2
("drm/mediatek: hdmi: Add optional limit on maximal HDMI mode clock")
another similar check was introduced.

Unfortunately though, at the time of writing, MT8173 does not provide
any mtk_hdmi_conf structure and this is crashing the kernel with NULL
pointer upon entering mtk_hdmi_bridge_mode_valid(), which happens as
soon as a HDMI cable gets plugged in.

To fix this regression, add a NULL pointer check for hdmi->conf in the
said function, restoring HDMI functionality and avoiding NULL pointer
kernel panics.

## References
- https://git.kernel.org/stable/c/3b8e19a0aa3933a785be9f1541afd8d398c4ec69
- https://git.kernel.org/stable/c/71d07ebc5000b9c1d140e99e7493b0bafa954776
