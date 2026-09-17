# [H] vt: stabilize tty reference in kbd_keycode with tty_port_tty_get

## Summary
Severity: High
Advisory: CVE-2026-74675
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74675
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vt: stabilize tty reference in kbd_keycode with tty_port_tty_get

kbd_keycode() reads vc->port.tty without acquiring a tty reference,
racing against con_shutdown() which clears port.tty under a different
lock. Use tty_port_tty_get()/tty_kref_put() to hold a proper reference
for the duration the tty pointer is needed.

## References
- https://git.kernel.org/stable/c/38400673c9bfb39cfc87539e1a072087e98f4e4f
- https://git.kernel.org/stable/c/38a0aa593ebc275aea6f79534d07f44e43768ce6
- https://git.kernel.org/stable/c/3f6b1d3fcfc26dc3fc85262f753439df93b055b4
- https://git.kernel.org/stable/c/b664592e9ba8c47c9e23408db7ba52eb9f946c8a
- https://git.kernel.org/stable/c/b84fd400f80adf4d1c88fbce50ae1cf2f8119e65
- https://git.kernel.org/stable/c/cab5a342f0589334046741006d8a280514f94235
- https://git.kernel.org/stable/c/cc4a1a2ce0c58eafd477effb055863935260ddc1
- https://git.kernel.org/stable/c/e25d47a526939ad44b75f778b8a7500562b84fc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74675.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
