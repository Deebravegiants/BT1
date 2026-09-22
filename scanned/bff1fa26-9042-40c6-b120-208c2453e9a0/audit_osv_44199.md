# [H] fbdev: clear fb_info->mode before deleting a videomode

## Summary
Severity: High
Advisory: CVE-2026-80579
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80579
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: clear fb_info->mode before deleting a videomode

fb_set_var() can delete a mode from info->modelist when userspace
passes FB_ACTIVATE_INV_MODE through FBIOPUT_VSCREENINFO. The code
checks that the mode being deleted is not the current info->var and
that fbcon is not using it, but it does not check fb_info->mode.

fb_info->mode may still point into the modelist entry being deleted.
If the entry is freed, later mode sysfs reads through show_mode() can
dereference a stale pointer.

Clear fb_info->mode before calling fb_delete_videomode() when it
matches the mode being removed.

## References
- https://git.kernel.org/stable/c/95e647d2a5304a8fd11f1ba3c8502de700650131
- https://git.kernel.org/stable/c/ce7fef961c63229b22dec415fb988899f479d61f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80579.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80579
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
