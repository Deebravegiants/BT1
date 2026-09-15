# [H] rxrpc: Fix the reception of a reply packet before data transmission

## Summary
Severity: High
Advisory: CVE-2026-74429
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74429
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix the reception of a reply packet before data transmission

Fix rxrpc_receiving_reply() to handle the reception of an apparent reply
DATA packet before rxrpc has had a chance to send any request DATA packets
on a client call by checking to see if the call has been exposed yet by
sending the first packet.

Without this, rxrpc_rotate_tx_window() might oops.

Also fix rxrpc_rotate_tx_window() to handle the Tx queue being empty by
changing the do...while loop into a while loop, just in case a call is
abnormally terminated by an early reply before the last request packet is
transmitted.

## References
- https://git.kernel.org/stable/c/a58e33405acd2584e730c1da72635f822ada6b49
- https://git.kernel.org/stable/c/e220ae559e5a0fc33e41ec6a348ea50387cb8b0f
- https://git.kernel.org/stable/c/f9be514984471ff0003738b2e1efed12bc3433ff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74429.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74429
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
