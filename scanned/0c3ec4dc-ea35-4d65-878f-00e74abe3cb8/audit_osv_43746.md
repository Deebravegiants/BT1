# [H] packet: use consistent hard_header_len in TX_RING send path

## Summary
Severity: High
Advisory: CVE-2026-74668
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74668
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

packet: use consistent hard_header_len in TX_RING send path

tpacket_snd() reads dev->hard_header_len independently for skb
allocation and header construction in tpacket_fill_skb(). Concurrent
netdevice reconfiguration can therefore make the reserved headroom
smaller than the amount later pushed, or make copylen - hard_header_len
negative.

Snapshot hard_header_len once before processing ring frames and use it
for the frame limit, headroom allocation, copy length, and skb
construction. Pass the snapshot to tpacket_fill_skb().

The separate SOCK_DGRAM consistency problem between hard_header_len and
header_ops->create is not addressed here.

## References
- https://git.kernel.org/stable/c/016763e829cac37b3234eace86fd0a4c560de4a7
- https://git.kernel.org/stable/c/21b5953e7494c16a42e6cd8cf110e18d13ae4a6b
- https://git.kernel.org/stable/c/27e068d1b35dbec10a3cf268887c94407be4badc
- https://git.kernel.org/stable/c/2a73b2c37ee3060a880b53cd24783d93fc7be5f8
- https://git.kernel.org/stable/c/9c7e8ff48c377bef18c3d178748aea0575b69ede
- https://git.kernel.org/stable/c/d48ea5c9c4c34dc0df621f0e39ed3a16b644621a
- https://git.kernel.org/stable/c/d85d2fd54e901637c81d847811e03c662aee13cd
- https://git.kernel.org/stable/c/e79f59a8527a49078cfaf8fe8fb5fcefc20c76d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74668.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74668
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
