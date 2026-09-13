# [H] hwmon: (pmbus/adm1266) include PEC byte in pmbus_block_xfer read buffer

## Summary
Severity: High
Advisory: CVE-2026-64086
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64086
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus/adm1266) include PEC byte in pmbus_block_xfer read buffer

adm1266_pmbus_block_xfer() sets up the read transaction with

	.buf = data->read_buf,
	.len = ADM1266_PMBUS_BLOCK_MAX + 2,

but read_buf in struct adm1266_data is declared as

	u8 read_buf[ADM1266_PMBUS_BLOCK_MAX + 1];

For a max-length block response (length byte = 255 + up to 1 PEC
byte), the i2c controller is told to write 257 bytes into a 256-byte
buffer, putting one byte past the end of read_buf.  The same response
also makes the subsequent PEC compare

	if (crc != msgs[1].buf[msgs[1].buf[0] + 1])

read a byte beyond the array.

Bump the read_buf declaration to ADM1266_PMBUS_BLOCK_MAX + 2 so the
buffer can hold the length byte, up to 255 payload bytes, and the PEC
byte the i2c_msg length already accounts for.

## References
- https://git.kernel.org/stable/c/2279c342d94eca225bf9f301c8806a05a1c81619
- https://git.kernel.org/stable/c/397d3f523bfff2f4e3dacf9b1339bd76dc207f78
- https://git.kernel.org/stable/c/472744f69d25a2d5111ad62f1d62579dce2c13c8
- https://git.kernel.org/stable/c/487566cb1ccdf3756fdd7bf8d875e612ff3169bb
- https://git.kernel.org/stable/c/528a9f88e88502d0c2f2052a279415074cd83715
- https://git.kernel.org/stable/c/a6c802145a8de0830bca803c6d415f7e9e683624
- https://git.kernel.org/stable/c/bd5be3fa5de6dbf61f1b3cec6b79c2c2f8065694
- https://git.kernel.org/stable/c/d94ceb16e55b6d8019ab069e357c76ac42f0ffbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64086.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64086
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
