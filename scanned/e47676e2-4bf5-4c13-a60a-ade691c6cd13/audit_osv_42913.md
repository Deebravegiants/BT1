# [H] i2c: imx: fix locked bus on SMBus block-read of 0 (IRQ)

## Summary
Severity: High
Advisory: CVE-2026-72141
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72141
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: imx: fix locked bus on SMBus block-read of 0 (IRQ)

SMBus 3.1 6.5.7 allows a Block Read byte count of 0, but the
interrupt-driven block-read state machine rejects it as -EPROTO. Worse,
it returns without a NACK+STOP: the next receive cycle has already
started, so the target keeps holding SDA and the bus stays stuck until a
power cycle of this i2c controller.

Accept count=0: NACK the in-flight dummy byte (TXAK) and set msg->len to
2 so i2c_imx_isr_read_continue() emits STOP via its normal last-byte
path. The dummy byte is discarded; block-read callers only consume
buf[0..count-1].

Reading I2DR has likewise already armed the next byte on the
count > I2C_SMBUS_BLOCK_MAX error path, so NACK it (TXAK) before aborting
with -EPROTO; otherwise the failing transfer's STOP cannot complete and
the bus stays held.

The atomic path regressed earlier (v3.16) and is fixed separately; this
patch covers only the v6.13 state-machine rework.

## References
- https://git.kernel.org/stable/c/07fd9385f0d87dff4b34f355f68adf701080cb24
- https://git.kernel.org/stable/c/56ddfc18ea8f7d77747658892873eb632b2ed530
- https://git.kernel.org/stable/c/5d3240f42a667e29262aff76fdebfcdac4980626
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72141.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
