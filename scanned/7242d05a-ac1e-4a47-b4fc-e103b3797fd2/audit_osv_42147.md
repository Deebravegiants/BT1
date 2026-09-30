# [H] net: ethernet: arc: emac: quiesce interrupts before requesting IRQ

## Summary
Severity: High
Advisory: CVE-2026-64587
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64587
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: arc: emac: quiesce interrupts before requesting IRQ

Normal RX/TX interrupts are enabled later, in arc_emac_open(), so probe
should not see interrupt delivery in the usual case. However, hardware may
still present stale or latched interrupt status left by firmware or the
bootloader.

If probe later unwinds after devm_request_irq() has installed the handler,
such a stale interrupt can still reach arc_emac_intr() during teardown and
race with release of the associated net_device.

Avoid that window by putting the device into a known quiescent state before
requesting the IRQ: disable all EMAC interrupt sources and clear any
pending EMAC interrupt status bits. This keeps the change hardware-focused
and minimal, while preventing spurious IRQ delivery from leftover state.

## References
- https://git.kernel.org/stable/c/2503d08f8a2de618e5c3a8183b250ff4a2e2d52c
- https://git.kernel.org/stable/c/5f29dd540fe5ea3c826fc8ec759ba488b31f9707
- https://git.kernel.org/stable/c/6fc7449773748c7b904235a09a67054d78ab1172
- https://git.kernel.org/stable/c/81431da777924dddaefa5c9b0ca9da4a93f9df96
- https://git.kernel.org/stable/c/8efd5dcd31e22a9308b16b107a052fcd568c0a99
- https://git.kernel.org/stable/c/8f9adb3605e36f75639de529bb3d66e94194a388
- https://git.kernel.org/stable/c/abd338da658d7faa8e26cfefc8f83f0066707564
- https://git.kernel.org/stable/c/d0f2386f529807826e7404d40a245ee428f89f62
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64587.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64587
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
