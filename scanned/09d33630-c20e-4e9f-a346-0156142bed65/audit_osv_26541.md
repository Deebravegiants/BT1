# [M] drm/mediatek: dp: Change logging to dev for mtk_dp_aux_transfer()

## Summary
Severity: Medium
Advisory: CVE-2023-53325
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53325
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: dp: Change logging to dev for mtk_dp_aux_transfer()

Change logging from drm_{err,info}() to dev_{err,info}() in functions
mtk_dp_aux_transfer() and mtk_dp_aux_do_transfer(): this will be
essential to avoid getting NULL pointer kernel panics if any kind
of error happens during AUX transfers happening before the bridge
is attached.

This may potentially start happening in a later commit implementing
aux-bus support, as AUX transfers will be triggered from the panel
driver (for EDID) before the mtk-dp bridge gets attached, and it's
done in preparation for the same.

## References
- https://git.kernel.org/stable/c/4c743c1dd2ee2a72951660b6798d4d7f7674f87b
- https://git.kernel.org/stable/c/7839f62294039959076dd06232e07aec7f7d5b2b
- https://git.kernel.org/stable/c/fd70e2019bfbcb0ed90c5e23839bf510ce6acf8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53325.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
