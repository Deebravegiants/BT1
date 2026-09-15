# [H] Bluetooth: l2cap: Check encryption key size on incoming connection

## Summary
Severity: High
Advisory: CVE-2025-39889
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-39889
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: l2cap: Check encryption key size on incoming connection

This is required for passing GAP/SEC/SEM/BI-04-C PTS test case:
  Security Mode 4 Level 4, Responder - Invalid Encryption Key Size
  - 128 bit

This tests the security key with size from 1 to 15 bytes while the
Security Mode 4 Level 4 requests 16 bytes key size.

Currently PTS fails with the following logs:
- expected:Connection Response:
    Code: [3 (0x03)] Code
    Identifier: (lt)WildCard: Exists(gt)
    Length: [8 (0x0008)]
    Destination CID: (lt)WildCard: Exists(gt)
    Source CID: [64 (0x0040)]
    Result: [3 (0x0003)] Connection refused - Security block
    Status: (lt)WildCard: Exists(gt),
but received:Connection Response:
    Code: [3 (0x03)] Code
    Identifier: [1 (0x01)]
    Length: [8 (0x0008)]
    Destination CID: [64 (0x0040)]
    Source CID: [64 (0x0040)]
    Result: [0 (0x0000)] Connection Successful
    Status: [0 (0x0000)] No further information available

And HCI logs:
< HCI Command: Read Encrypti.. (0x05|0x0008) plen 2
        Handle: 14 Address: 00:1B:DC:F2:24:10 (Vencer Co., Ltd.)
> HCI Event: Command Complete (0x0e) plen 7
      Read Encryption Key Size (0x05|0x0008) ncmd 1
        Status: Success (0x00)
        Handle: 14 Address: 00:1B:DC:F2:24:10 (Vencer Co., Ltd.)
        Key size: 7
> ACL Data RX: Handle 14 flags 0x02 dlen 12
      L2CAP: Connection Request (0x02) ident 1 len 4
        PSM: 4097 (0x1001)
        Source CID: 64
< ACL Data TX: Handle 14 flags 0x00 dlen 16
      L2CAP: Connection Response (0x03) ident 1 len 8
        Destination CID: 64
        Source CID: 64
        Result: Connection successful (0x0000)
        Status: No further information available (0x0000)

## References
- https://git.kernel.org/stable/c/24b2cdfc16e9bd6ab3d03b8e01c590755bd3141f
- https://git.kernel.org/stable/c/522e9ed157e3c21b4dd623c79967f72c21e45b78
- https://git.kernel.org/stable/c/9e3114958d87ea88383cbbf38c89e04b8ea1bce5
- https://git.kernel.org/stable/c/c6d527bbd3d3896375079f5dbc8b7f96734a3ba5
- https://git.kernel.org/stable/c/d49798ecd26e0ee7995a7fc1e90ca5cd9b4402d6
- https://git.kernel.org/stable/c/d4ca2fd218caafbf50e3343ba1260c6a23b5676a
- https://git.kernel.org/stable/c/ed503d340a501e414114ddc614a3aae4f6e9eae2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39889.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
