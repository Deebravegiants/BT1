# [H] drm/xe/guc: Check GuC running state before deregistering exec queue

## Summary
Severity: High
Advisory: CVE-2025-40166
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40166
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc: Check GuC running state before deregistering exec queue

In normal operation, a registered exec queue is disabled and
deregistered through the GuC, and freed only after the GuC confirms
completion. However, if the driver is forced to unbind while the exec
queue is still running, the user may call exec_destroy() after the GuC
has already been stopped and CT communication disabled.

In this case, the driver cannot receive a response from the GuC,
preventing proper cleanup of exec queue resources. Fix this by directly
releasing the resources when GuC is not running.

Here is the failure dmesg log:
"
[  468.089581] ---[ end trace 0000000000000000 ]---
[  468.089608] pci 0000:03:00.0: [drm] *ERROR* GT0: GUC ID manager unclean (1/65535)
[  468.090558] pci 0000:03:00.0: [drm] GT0:     total 65535
[  468.090562] pci 0000:03:00.0: [drm] GT0:     used 1
[  468.090564] pci 0000:03:00.0: [drm] GT0:     range 1..1 (1)
[  468.092716] ------------[ cut here ]------------
[  468.092719] WARNING: CPU: 14 PID: 4775 at drivers/gpu/drm/xe/xe_ttm_vram_mgr.c:298 ttm_vram_mgr_fini+0xf8/0x130 [xe]
"

v2: use xe_uc_fw_is_running() instead of xe_guc_ct_enabled().
    As CT may go down and come back during VF migration.

(cherry picked from commit 9b42321a02c50a12b2beb6ae9469606257fbecea)

## References
- https://git.kernel.org/stable/c/2c6e5904c5bdbac8e0eadee40f70c42bb83f6dc6
- https://git.kernel.org/stable/c/9f64b3cd051b825de0a2a9f145c8e003200cedd5
- https://git.kernel.org/stable/c/fa708415566bbe5361c935645107319f8edc8dc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40166.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40166
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
