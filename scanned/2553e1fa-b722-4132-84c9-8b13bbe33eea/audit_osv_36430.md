# [H] drm/xe: Open-code GGTT MMIO access protection

## Summary
Severity: High
Advisory: CVE-2026-23466
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23466
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Open-code GGTT MMIO access protection

GGTT MMIO access is currently protected by hotplug (drm_dev_enter),
which works correctly when the driver loads successfully and is later
unbound or unloaded. However, if driver load fails, this protection is
insufficient because drm_dev_unplug() is never called.

Additionally, devm release functions cannot guarantee that all BOs with
GGTT mappings are destroyed before the GGTT MMIO region is removed, as
some BOs may be freed asynchronously by worker threads.

To address this, introduce an open-coded flag, protected by the GGTT
lock, that guards GGTT MMIO access. The flag is cleared during the
dev_fini_ggtt devm release function to ensure MMIO access is disabled
once teardown begins.

(cherry picked from commit 4f3a998a173b4325c2efd90bdadc6ccd3ad9a431)

## References
- https://git.kernel.org/stable/c/01f2557aa684e514005541e71a3d01f4cd45c170
- https://git.kernel.org/stable/c/1e9e2640d870d4837bcfdc220cb2c99ae5ee119f
- https://git.kernel.org/stable/c/76326dc06d8793c2c81c31cc0115dbc348de2f88
- https://git.kernel.org/stable/c/e2b424aadecb640f9e037b2891191cf8fd4c64cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23466.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23466
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
