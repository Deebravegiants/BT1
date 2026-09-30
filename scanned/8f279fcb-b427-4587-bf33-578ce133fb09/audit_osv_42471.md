# [H] media: stm32: dcmi: unregister notifier on probe failure

## Summary
Severity: High
Advisory: CVE-2026-68210
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68210
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: stm32: dcmi: unregister notifier on probe failure

dcmi_graph_init() registers the async notifier before dcmi_probe() toggles
the reset line. If reset_control_assert() or reset_control_deassert()
fails afterwards, probe returns through err_cleanup and the driver core
will not call dcmi_remove().

Unregister the notifier before cleaning it up on that error path,
matching the successful remove path and the V4L2 async notifier lifetime
rules.

[hverkuil: added Fixes tag]

## References
- https://git.kernel.org/stable/c/084973ebd67b28f0945c5d45408f86c58b540110
- https://git.kernel.org/stable/c/222a9301b086852b90d3b092fef436c3f4e927c4
- https://git.kernel.org/stable/c/37ff63c5d7119cbc5c6bacdcc658add6008a8e1f
- https://git.kernel.org/stable/c/4b7ee504969e074725e439c949f2483e5fa5572a
- https://git.kernel.org/stable/c/6c6f22b7e6cbc4e8c1e359fc9b190419391c3db7
- https://git.kernel.org/stable/c/931abe1deb65b919d23fa203d7f6d6fbd4fccd8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68210.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
