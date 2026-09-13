# [H] Bluetooth: hci_event: validate skb length for unknown CC opcode

## Summary
Severity: High
Advisory: CVE-2025-40301
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40301
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: validate skb length for unknown CC opcode

In hci_cmd_complete_evt(), if the command complete event has an unknown
opcode, we assume the first byte of the remaining skb->data contains the
return status. However, parameter data has previously been pulled in
hci_event_func(), which may leave the skb empty. If so, using skb->data[0]
for the return status uses un-init memory.

The fix is to check skb->len before using skb->data.

## References
- https://git.kernel.org/stable/c/1a0ddaaf97405dbd11d4cb5a961a3f82400e8a50
- https://git.kernel.org/stable/c/5c5f1f64681cc889d9b13e4a61285e9e029d6ab5
- https://git.kernel.org/stable/c/779f83a91d4f1bf5ddfeaf528420cbb6dbf03fa8
- https://git.kernel.org/stable/c/cf2c2acec1cf456c3d11c11a7589e886a0f963a9
- https://git.kernel.org/stable/c/fea895de78d3bb2f0c09db9f10b18f8121b15759
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40301.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40301
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
