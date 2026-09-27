# [H] net: ppp: Add bound checking for skb data on ppp_sync_txmung

## Summary
Severity: High
Advisory: CVE-2025-37749
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37749
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ppp: Add bound checking for skb data on ppp_sync_txmung

Ensure we have enough data in linear buffer from skb before accessing
initial bytes. This prevents potential out-of-bounds accesses
when processing short packets.

When ppp_sync_txmung receives an incoming package with an empty
payload:
(remote) gef➤  p *(struct pppoe_hdr *) (skb->head + skb->network_header)
$18 = {
	type = 0x1,
	ver = 0x1,
	code = 0x0,
	sid = 0x2,
        length = 0x0,
	tag = 0xffff8880371cdb96
}

from the skb struct (trimmed)
      tail = 0x16,
      end = 0x140,
      head = 0xffff88803346f400 "4",
      data = 0xffff88803346f416 ":\377",
      truesize = 0x380,
      len = 0x0,
      data_len = 0x0,
      mac_len = 0xe,
      hdr_len = 0x0,

it is not safe to access data[2].

[pabeni@redhat.com: fixed subj typo]

## References
- https://git.kernel.org/stable/c/1f6eb9fa87a781d5370c0de7794ae242f1a95ee5
- https://git.kernel.org/stable/c/529401c8f12ecc35f9ea5d946d5a5596cf172b48
- https://git.kernel.org/stable/c/6e8a6bf43cea4347121ab21bb1ed8d7bef7e732e
- https://git.kernel.org/stable/c/99aa698dec342a07125d733e39aab4394b3b7e05
- https://git.kernel.org/stable/c/aabc6596ffb377c4c9c8f335124b92ea282c9821
- https://git.kernel.org/stable/c/b4c836d33ca888695b2f2665f948bc1b34fbd533
- https://git.kernel.org/stable/c/b78f2b458f56a5a4d976c8e01c43dbf58d3ea2ca
- https://git.kernel.org/stable/c/de5a4f0cba58625e88b7bebd88f780c8c0150997
- https://git.kernel.org/stable/c/fbaffe8bccf148ece8ad67eb5d7aa852cabf59c8
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37749.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37749
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
