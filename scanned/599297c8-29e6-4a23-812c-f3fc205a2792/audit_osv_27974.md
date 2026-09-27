# [H] soc: qcom: pmic_glink_altmode: fix drm bridge use-after-free

## Summary
Severity: High
Advisory: CVE-2024-26909
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26909
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.23, >=6.7.0 <6.7.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: qcom: pmic_glink_altmode: fix drm bridge use-after-free

A recent DRM series purporting to simplify support for "transparent
bridges" and handling of probe deferrals ironically exposed a
use-after-free issue on pmic_glink_altmode probe deferral.

This has manifested itself as the display subsystem occasionally failing
to initialise and NULL-pointer dereferences during boot of machines like
the Lenovo ThinkPad X13s.

Specifically, the dp-hpd bridge is currently registered before all
resources have been acquired which means that it can also be
deregistered on probe deferrals.

In the meantime there is a race window where the new aux bridge driver
(or PHY driver previously) may have looked up the dp-hpd bridge and
stored a (non-reference-counted) pointer to the bridge which is about to
be deallocated.

When the display controller is later initialised, this triggers a
use-after-free when attaching the bridges:

	dp -> aux -> dp-hpd (freed)

which may, for example, result in the freed bridge failing to attach:

	[drm:drm_bridge_attach [drm]] *ERROR* failed to attach bridge /soc@0/phy@88eb000 to encoder TMDS-31: -16

or a NULL-pointer dereference:

	Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000
	...
	Call trace:
	  drm_bridge_attach+0x70/0x1a8 [drm]
	  drm_aux_bridge_attach+0x24/0x38 [aux_bridge]
	  drm_bridge_attach+0x80/0x1a8 [drm]
	  dp_bridge_init+0xa8/0x15c [msm]
	  msm_dp_modeset_init+0x28/0xc4 [msm]

The DRM bridge implementation is clearly fragile and implicitly built on
the assumption that bridges may never go away. In this case, the fix is
to move the bridge registration in the pmic_glink_altmode driver to
after all resources have been looked up.

Incidentally, with the new dp-hpd bridge implementation, which registers
child devices, this is also a requirement due to a long-standing issue
in driver core that can otherwise lead to a probe deferral loop (see
commit fbc35b45f9f6 ("Add documentation on meaning of -EPROBE_DEFER")).

[DB: slightly fixed commit message by adding the word 'commit']

## References
- https://git.kernel.org/stable/c/2bbd65c6ca567ed8dbbfc4fb945f57ce64bef342
- https://git.kernel.org/stable/c/b979f2d50a099f3402418d7ff5f26c3952fb08bb
- https://git.kernel.org/stable/c/ef45aa2841e15b649e5417fe3d4de395fe462781
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26909.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
