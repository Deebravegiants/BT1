# [H] packet: use consistent hard_header_len in non-ring send paths

## Summary
Severity: High
Advisory: CVE-2026-74582
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-74582
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

packet: use consistent hard_header_len in non-ring send paths

packet_snd() reads dev->hard_header_len multiple times while allocating
and constructing an skb. Device reconfiguration can change this value
concurrently, for example through bonding device type changes.

For SOCK_RAW, packet_snd() can save a larger value in reserve and later
allocate headroom using a smaller value. Moving skb->data back by reserve
then places it before skb->head, and the following copy from userspace can
attempt an out-of-bounds write.

packet_sendmsg_spkt() has the same issue because it calculates its
reservation and header offset from separate reads before dropping the RCU
read lock to allocate the skb.

Add LL_RESERVED_SPACE_EX() for callers that already saved a header length.
Read hard_header_len once in packet_snd() and use it for allocation and
construction. In packet_sendmsg_spkt(), preserve the allocation-time value
through the device lookup retry.

The separate SOCK_DGRAM consistency problem between hard_header_len and
header_ops->create is not addressed here.

## References
- https://git.kernel.org/stable/c/03390aa32e669cc4ecd7d34108e2e1afc13d689d
- https://git.kernel.org/stable/c/142e287b3a25cfe909215177c23243e7fc5ae2b1
- https://git.kernel.org/stable/c/5bb10753d428aadfc356a2bfe9acea09c82a62ec
- https://git.kernel.org/stable/c/78a47127e33c340bc6d38dcc4552a094b4f5cc77
- https://git.kernel.org/stable/c/9052756290962ffb9a661bcf319e92dedaaedfed
- https://git.kernel.org/stable/c/91f041451f967cd87ed722a8f43c0b767a64f1a0
- https://git.kernel.org/stable/c/b06b6fce6d7deaf7238e09b48ce3b1125ff41acd
- https://git.kernel.org/stable/c/bcd4df60ac9481b1ceffdfe5ec38fe51dcaae812
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74582.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74582
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
