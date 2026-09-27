# [H] mtd: mchp23k256: use SPI match data for chip caps

## Summary
Severity: High
Advisory: CVE-2026-68467
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68467
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: mchp23k256: use SPI match data for chip caps

The driver stores chip capacity information in both the OF match table
and the SPI id table. Probe currently uses of_device_get_match_data(),
so a non-OF SPI modalias match falls back to mchp23k256_caps even when
the SPI id table selected a different part.

Use spi_get_device_match_data() so SPI id-table driver_data is consumed
when OF match data is absent. This keeps the existing default fallback
while avoiding the wrong MTD geometry for id-table-only matches.

## References
- https://git.kernel.org/stable/c/04ebd3766861f219325852c9598e0f0281cb3636
- https://git.kernel.org/stable/c/09e044192a42f716215fbd1a100ee87fa57426aa
- https://git.kernel.org/stable/c/2e179b028da9fd628a09286a2c9df4fa076b2cc9
- https://git.kernel.org/stable/c/7c0a3a73dccc9a3fc701f6be762449f18d0ca0fc
- https://git.kernel.org/stable/c/a0c38083623c8b210a5b87fd34bebd05aa935ae8
- https://git.kernel.org/stable/c/d322e40f4edf92bf0ca329e5aa4ae1c0316feb38
- https://git.kernel.org/stable/c/dbe2254d1da99c986f9a3392471fc5eaa3229647
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68467.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68467
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
