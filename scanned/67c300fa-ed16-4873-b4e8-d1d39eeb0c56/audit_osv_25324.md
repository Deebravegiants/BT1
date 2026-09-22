# [H] RIOT-OS vulnerable to Race Condition in SFR Timeout

## Summary
Severity: High
Advisory: CVE-2023-33974
Aliases: GHSA-8m3w-mphf-wxm8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33974
Type: osv

## Details
RIOT-OS, an operating system for Internet of Things (IoT) devices, contains a network stack with the ability to process 6LoWPAN frames. In versions 2023.01 and prior, an attacker can send multiple crafted frames to the device to trigger a race condition. The race condition invalidates assumptions about the program state and leads to an invalid memory access resulting in denial of service. This issue is patched in pull request 19679. There are no known workarounds.

## References
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L1717
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L509
- https://github.com/RIOT-OS/RIOT/blob/f41b4b67b6affca0a8b32edced7f51088696869a/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L617
- https://github.com/RIOT-OS/RIOT/blob/master/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L1586
- https://github.com/RIOT-OS/RIOT/blob/master/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L404
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33974.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-8m3w-mphf-wxm8
- https://nvd.nist.gov/vuln/detail/CVE-2023-33974
- https://github.com/RIOT-OS/RIOT/commit/31c6191f6196f1a05c9765cffeadba868e3b0723
- https://github.com/RIOT-OS/RIOT/pull/19679
