# [C] batman-adv: reject oversized global TT response buffers

## Summary
Severity: Critical
Advisory: CVE-2026-31659
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31659
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: reject oversized global TT response buffers

batadv_tt_prepare_tvlv_global_data() builds the allocation length for a
global TT response in 16-bit temporaries. When a remote originator
advertises a large enough global TT, the TT payload length plus the VLAN
header offset can exceed 65535 and wrap before kmalloc().

The full-table response path still uses the original TT payload length when
it fills tt_change, so the wrapped allocation is too small and
batadv_tt_prepare_tvlv_global_data() writes past the end of the heap object
before the later packet-size check runs.

Fix this by rejecting TT responses whose TVLV value length cannot fit in
the 16-bit TVLV payload length field.

## References
- https://git.kernel.org/stable/c/2997f4bd1f982e7013709946e00be89b507693fa
- https://git.kernel.org/stable/c/3a359bf5c61d52e7f09754108309d637532164a6
- https://git.kernel.org/stable/c/69d61639bc7e963c3b645e570279d731e7c89062
- https://git.kernel.org/stable/c/7e5d007e0df946bffb8542fb112e0044014a5897
- https://git.kernel.org/stable/c/95c71365a2222908441b54d6f2c315e0c79fcec3
- https://git.kernel.org/stable/c/cf2199171ef799ca7270019125f4a91bd20ad4d9
- https://git.kernel.org/stable/c/de6c1dc3c7d01a152607e6fcecee4d5288283f10
- https://git.kernel.org/stable/c/f970646b9a39539d1bac86822ac78b5915455ea9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31659.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31659
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
