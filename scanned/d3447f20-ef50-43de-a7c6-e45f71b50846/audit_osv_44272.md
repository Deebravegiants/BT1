# [H] spi: spi-qpic-snand: write the feature value before executing SET_FEATURE

## Summary
Severity: High
Advisory: CVE-2026-80712
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80712
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-qpic-snand: write the feature value before executing SET_FEATURE

qcom_spi_send_cmdaddr() programs NAND_FLASH_CMD/NAND_EXEC_CMD and submits
the descriptors, which makes the controller execute the command
immediately. For SPINAND_SET_FEATURE the value to be written is only
placed into NAND_FLASH_FEATURES afterwards, by qcom_spi_io_op(), in a
second submission - so the chip is programmed with whatever that register
happened to hold from a previous operation, and the intended value is only
applied by the *next* SET_FEATURE.

Measured on a TP-Link Archer AX55 v1 (IPQ5018, ESMT F50L1G41LB): writing
0x40 to the configuration register (0xb0) leaves the chip at 0x00, and the
subsequent write of 0x00 leaves it at 0x40 - every write lands one
operation late.

This stayed unnoticed until v6.18 added SPI-NAND OTP support together
with OTP entries for ESMT chips. spinand_otp_rw() enables OTP mode,
reads, and disables it again, and mtd_otp_nvmem_add() does this during
MTD registration. With the off-by-one, the "disable" write actually
applies the previously requested value, so CFG_OTP_ENABLE ends up set:
the chip stays in OTP mode, every subsequent array read returns the OTP
area instead of the array (UBI reports an empty device) and all writes
fail with -EIO because the OTP area is write protected. On this board
that makes the whole flash unusable and the device unbootable.

Write the feature value into NAND_FLASH_FEATURES as part of the same
transaction, before NAND_EXEC_CMD. While at it, copy only the bytes the
operation actually carries - the previous code dereferenced a 4-byte
pointer on a one-byte buffer (spinand->scratchbuf).

With this patch the flash contents read back bit-identical to a
known-good dump of the same board taken under the vendor firmware
(md5-verified across partitions), and writes work.

## References
- https://git.kernel.org/stable/c/3ba021079ef2ac6e21e3547328496ac42d22b56a
- https://git.kernel.org/stable/c/581e5166f0780103dc91c0d8ebc801f9af4824b0
- https://git.kernel.org/stable/c/8fd62901d6bf03f274a49dd0060793cc07dd51b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80712.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
