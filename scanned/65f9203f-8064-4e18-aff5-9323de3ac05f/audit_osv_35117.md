# [H] spi: ch341: fix out-of-bounds memory access in ch341_transfer_one

## Summary
Severity: High
Advisory: CVE-2025-68352
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68352
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: ch341: fix out-of-bounds memory access in ch341_transfer_one

Discovered by Atuin - Automated Vulnerability Discovery Engine.

The 'len' variable is calculated as 'min(32, trans->len + 1)',
which includes the 1-byte command header.

When copying data from 'trans->tx_buf' to 'ch341->tx_buf + 1', using 'len'
as the length is incorrect because:

1. It causes an out-of-bounds read from 'trans->tx_buf' (which has size
   'trans->len', i.e., 'len - 1' in this context).
2. It can cause an out-of-bounds write to 'ch341->tx_buf' if 'len' is
   CH341_PACKET_LENGTH (32). Writing 32 bytes to ch341->tx_buf + 1
   overflows the buffer.

Fix this by copying 'len - 1' bytes.

## References
- https://git.kernel.org/stable/c/545d1287e40a55242f6ab68bcc1ba3b74088b1bc
- https://git.kernel.org/stable/c/81841da1f30f66a850cc8796d99ba330aad9d696
- https://git.kernel.org/stable/c/cad6c0fd6f3c0e76a1f75df4bce3b08a13f08974
- https://git.kernel.org/stable/c/ea1e43966cd03098fcd5f0d72e6c2901d45fa08d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68352.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68352
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
