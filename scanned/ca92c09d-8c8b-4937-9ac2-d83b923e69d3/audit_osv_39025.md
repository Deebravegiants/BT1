# [H] hwmon: (pmbus/q54sj108a2) fix stack overflow in debugfs read

## Summary
Severity: High
Advisory: CVE-2026-43380
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43380
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus/q54sj108a2) fix stack overflow in debugfs read

The q54sj108a2_debugfs_read function suffers from a stack buffer overflow
due to incorrect arguments passed to bin2hex(). The function currently
passes 'data' as the destination and 'data_char' as the source.

Because bin2hex() converts each input byte into two hex characters, a
32-byte block read results in 64 bytes of output. Since 'data' is only
34 bytes (I2C_SMBUS_BLOCK_MAX + 2), this writes 30 bytes past the end
of the buffer onto the stack.

Additionally, the arguments were swapped: it was reading from the
zero-initialized 'data_char' and writing to 'data', resulting in
all-zero output regardless of the actual I2C read.

Fix this by:
1. Expanding 'data_char' to 66 bytes to safely hold the hex output.
2. Correcting the bin2hex() argument order and using the actual read count.
3. Using a pointer to select the correct output buffer for the final
   simple_read_from_buffer call.

## References
- https://git.kernel.org/stable/c/24a7b9daa103fa963b3fd37d8805b23e01621976
- https://git.kernel.org/stable/c/25dd70a03b1f5f3aa71e1a5091ecd9cd2a13ee43
- https://git.kernel.org/stable/c/52db5ef163c96f916d424e472fb17aadc35a9f7a
- https://git.kernel.org/stable/c/73a7a345816946d276ad2c46c8bb771de67cfc46
- https://git.kernel.org/stable/c/a0fc1b9c738fba231f190ab960c83202722efee5
- https://git.kernel.org/stable/c/b48a0f8d4541a4f6651dc9a64430ce9fdf5c120b
- https://git.kernel.org/stable/c/c59090c50f62a17129fc4c5407bc4071305a9e82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
