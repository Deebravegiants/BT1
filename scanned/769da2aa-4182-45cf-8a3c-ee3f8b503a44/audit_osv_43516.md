# [H] Bluetooth: hci: validate codec capability element length

## Summary
Severity: High
Advisory: CVE-2026-74300
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74300
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci: validate codec capability element length

Read Local Codec Capabilities returns a sequence of capability elements.
Each element starts with a one-byte length followed by that many payload
bytes.

hci_read_codec_capabilities() checks that the skb contains the length
byte, but then validates only caps->len against the remaining skb
length.  A malformed controller response with one remaining byte and
caps->len set to one passes that check even though the element needs two
bytes.  The parser then records a two-byte capability and copies one
byte beyond the advertised response payload into the codec list.

Validate the full element size, including the length byte, before adding
it to the accumulated capability length.  This preserves all well-formed
capability elements and drops only truncated controller responses.

## References
- https://git.kernel.org/stable/c/290b36f9d1eb9b2f72b40d826f26b4a182ab15f7
- https://git.kernel.org/stable/c/4bc16db0f11918e07edf9fdcda4a30cf4c9df45c
- https://git.kernel.org/stable/c/c38fbcdc407925c7088f7e5f11c1fff73d2d35a2
- https://git.kernel.org/stable/c/ec4d352747a62c1082f16c11a74b37d6eb85a5a3
- https://git.kernel.org/stable/c/f2ad01f55e07f9531efcea736087e6b8658a3440
- https://git.kernel.org/stable/c/fc97fc8cf7f53fd3619db63e09050d20a3a0c4b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74300.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
