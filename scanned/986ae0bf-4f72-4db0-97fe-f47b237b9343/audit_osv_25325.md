# [C] RIOT-OS vulnerable to Out of Bounds Write in _rbuf_add

## Summary
Severity: Critical
Advisory: CVE-2023-33975
Aliases: GHSA-f6ff-g7mh-58q4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33975
Type: osv

## Details
RIOT-OS, an operating system for Internet of Things (IoT) devices, contains a network stack with the ability to process 6LoWPAN frames. In version 2023.01 and prior, an attacker can send a crafted frame to the device resulting in an out of bounds write in the packet buffer. The overflow can be used to corrupt other packets and the allocator metadata. Corrupting a pointer will easily lead to denial of service. While carefully manipulating the allocator metadata gives an attacker the possibility to write data to arbitrary locations and thus execute arbitrary code. This issue is fixed in pull request 19680. As a workaround, disable support for fragmented IP datagrams.

## References
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L320
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L388
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L463
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L467
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L480
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33975.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-f6ff-g7mh-58q4
- https://nvd.nist.gov/vuln/detail/CVE-2023-33975
- https://github.com/RIOT-OS/RIOT/commit/1aeb90ee5555ae78b567a6365ae4ab71bfd1404b
- https://github.com/RIOT-OS/RIOT/pull/19680
