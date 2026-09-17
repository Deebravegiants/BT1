# [H] dmaengine: tegra: Fix burst size calculation

## Summary
Severity: High
Advisory: CVE-2026-72149
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72149
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: tegra: Fix burst size calculation

Currently, the Tegra GPC DMA hardware requires the transfer length to
be a multiple of the max burst size configured for the channel. When a
client requests a transfer where the length is not evenly divisible by
the configured max burst size, the DMA hangs with partial burst at
the end.

Fix this by reducing the burst size to the largest power-of-2 value
that evenly divides the transfer length. For example, a 40-byte
transfer with a 16-byte max burst will now use an 8-byte burst
(40 / 8 = 5 complete bursts) instead of causing a hang.

This issue was observed with the PL011 UART driver where TX DMA
transfers of arbitrary lengths were stuck.

## References
- https://git.kernel.org/stable/c/4651df83b6c796daead3447e8fd874322918ee4f
- https://git.kernel.org/stable/c/6e37e9e230c7e848bd8e8cd4db15bb18bcf11ad1
- https://git.kernel.org/stable/c/735951baa311c66353405dcac39375dd66441db0
- https://git.kernel.org/stable/c/7926c1e4be86379945fb5f168888ac4d2aaf6c91
- https://git.kernel.org/stable/c/8f0f5de1091119679d87f60dfb1acbff4b2a0ed3
- https://git.kernel.org/stable/c/a3b76b54e06d73166af4d1a284a0e0711889060c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72149.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
