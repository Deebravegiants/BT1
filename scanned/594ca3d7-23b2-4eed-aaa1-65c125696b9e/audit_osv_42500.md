# [H] vmxnet3: fix BUG_ON in vmxnet3_get_hdr_len() for Geneve packets

## Summary
Severity: High
Advisory: CVE-2026-68299
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68299
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

vmxnet3: fix BUG_ON in vmxnet3_get_hdr_len() for Geneve packets

vmxnet3_get_hdr_len() assumes gdesc->rcd.v4/v6/tcp always describe the
outer header, but for a Geneve-encapsulated packet the device can set
them based on the inner header instead, signalled by the
VMXNET3_RCD_HDR_INNER_SHIFT bit in the completion descriptor. Since the
function never skips the outer encapsulation, this mismatch triggers:

- BUG_ON(hdr.ipv4->protocol != IPPROTO_TCP), because the outer
  protocol is UDP (Geneve), not TCP.
- BUG_ON(hdr.eth->h_proto != ...), when the tunnel's outer and inner
  IP versions differ (e.g. outer IPv6/inner IPv4 or vice versa).

Check VMXNET3_RCD_HDR_INNER_SHIFT up front and bail out, since the
function cannot locate the inner header it would need to parse. Also
convert the remaining BUG_ON()s in this function to return 0
defensively.

## References
- https://git.kernel.org/stable/c/28cb5d8d13b4c1faf3f688f62e5df82fe7b438d8
- https://git.kernel.org/stable/c/28e382646417c7e2be9c9a7079eddf627ff52b90
- https://git.kernel.org/stable/c/2ddf51fcb6dd7d55ceef38e2e1a5ab2ab7fd47b0
- https://git.kernel.org/stable/c/34a71f5361fc3adb5b7138da78750b0d535a8252
- https://git.kernel.org/stable/c/4fdb0f162ccdbe9626863b10003855703253fa29
- https://git.kernel.org/stable/c/667b6e52048eaf4dbcf1707ed87ffd44abb9cb38
- https://git.kernel.org/stable/c/b28596baf87e25a078789f1c05817c8a3bf71257
- https://git.kernel.org/stable/c/fbab6b73cc086e32698c86e43d1b16bf17d24c36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68299.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68299
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
