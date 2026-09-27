# [H] HID: mcp2221: prevent a buffer overflow in mcp_smbus_write()

## Summary
Severity: High
Advisory: CVE-2022-50131
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50131
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: mcp2221: prevent a buffer overflow in mcp_smbus_write()

Smatch Warning:
drivers/hid/hid-mcp2221.c:388 mcp_smbus_write() error: __memcpy()
'&mcp->txbuf[5]' too small (59 vs 255)
drivers/hid/hid-mcp2221.c:388 mcp_smbus_write() error: __memcpy() 'buf'
too small (34 vs 255)

The 'len' variable can take a value between 0-255 as it can come from
data->block[0] and it is user data. So add an bound check to prevent a
buffer overflow in memcpy().

## References
- https://git.kernel.org/stable/c/3c0f8a59f2cc8841ee6653399a77f4f3e6e9a270
- https://git.kernel.org/stable/c/62ac2473553a00229e67bdf3cb023b62cf7f5a9a
- https://git.kernel.org/stable/c/6402116a7b5ec80fa40fd145a80c813019cd555f
- https://git.kernel.org/stable/c/66c8e816f2f2ca4a61b406503bd10bad1b35f72f
- https://git.kernel.org/stable/c/91443c669d280937968f0aa4edefa741cfe35314
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50131.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50131
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
