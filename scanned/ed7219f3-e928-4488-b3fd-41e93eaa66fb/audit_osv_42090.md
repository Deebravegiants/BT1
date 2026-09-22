# [H] ALSA: hda/cs35l41: Fix firmware load work teardown

## Summary
Severity: High
Advisory: CVE-2026-64481
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64481
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.97, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda/cs35l41: Fix firmware load work teardown

cs35l41_hda creates ALSA controls whose private data points at the
cs35l41_hda object. The firmware load control can also queue
fw_load_work.

Those controls are not removed on component unbind, and device remove
only cancels fw_load_work through cs35l41_remove_dsp(). That helper is
skipped when halo_initialized is false. With firmware_autostart
disabled, a firmware load can be requested before the DSP has been
initialized. If the component or device is removed before the queued
work runs, the worker can run after teardown and dereference driver
state that is no longer valid.

Track the created controls and remove them on unbind so no new control
callback can reach the driver data or queue more work. Then cancel
fw_load_work to drain any request that was already queued. Also cancel
the work unconditionally during device remove before runtime PM teardown.

## References
- https://git.kernel.org/stable/c/8947215c0136c9d905e4a46d824824f8b48a2e5b
- https://git.kernel.org/stable/c/b65020d5398f499c09498c9786dba6d67ae57664
- https://git.kernel.org/stable/c/ce0a903d0591e3e2c790c5b628802b08d1b287cc
- https://git.kernel.org/stable/c/d6a40a4d083ef74d00c8f9516cb5ff07ac70720b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64481.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
