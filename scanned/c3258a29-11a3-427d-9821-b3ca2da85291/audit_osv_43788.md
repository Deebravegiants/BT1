# [C] net: ethernet: ti: am65-cpsw-nuss: Fix port_id extraction from SRC TAG

## Summary
Severity: Critical
Advisory: CVE-2026-74737
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74737
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ti: am65-cpsw-nuss: Fix port_id extraction from SRC TAG

On the packet reception path, the ID of the MAC Port on which the packet
was received, is embedded in the RX DMA Descriptor's metadata. The ID is
extracted using the helper function cppi5_desc_get_tags_ids() which fills
in the 16-bit Source Tag into the 'port_id' variable. However, it is only
the lower 8-bits of the 16-bit Source Tag that represent the MAC Port ID,
while the upper 8-bits are Hardware-Reserved and carry an arbitrary value.
With the existing logic, sporadic kernel crash is observed due to the
subsequent driver code accessing out-of-bound memory because of an invalid
port_id.

Hence, fix the port_id extraction logic to use only the lower 8-bits of the
Source Tag as the MAC Port ID.

## References
- https://git.kernel.org/stable/c/14fc40bf28390e0ebee6a072457c36b82c614100
- https://git.kernel.org/stable/c/1c0e35ce761131f82062222779d8574849790892
- https://git.kernel.org/stable/c/36a05d2820077bb3955acb8111e1041d39148037
- https://git.kernel.org/stable/c/46a8e084a159e638ac2728e96980b65d752d65fd
- https://git.kernel.org/stable/c/551688b410d3fb0dae7739724422f268cd9446d6
- https://git.kernel.org/stable/c/72e4e3d7efc3b7d85f86abbe8b94f8e45074abe3
- https://git.kernel.org/stable/c/914e0100df3435bd14d09f397238e891cf9b7dce
- https://git.kernel.org/stable/c/9a220225efd6f58350bbb53fe70bdec08519267f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74737.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74737
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
