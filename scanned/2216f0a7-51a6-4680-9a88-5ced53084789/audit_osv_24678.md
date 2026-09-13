# [H] RIOT-OS vulnerable to NULL pointer dereference in gnrc_pktbuf_mark

## Summary
Severity: High
Advisory: CVE-2023-24825
Aliases: GHSA-xqm8-xj74-fjw2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-24825
Type: osv

## Details
RIOT-OS, an operating system for Internet of Things (IoT) devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2023.04, an attacker can send a crafted frame to the device to trigger a NULL pointer dereference leading to denial of service. This issue is fixed in version 2023.04. There are no known workarounds.

## References
- https://github.com/RIOT-OS/RIOT/blob/2022.10-branch/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L416
- https://github.com/RIOT-OS/RIOT/blob/2022.10-branch/sys/net/gnrc/network_layer/sixlowpan/frag/rb/gnrc_sixlowpan_frag_rb.c#L429
- https://github.com/RIOT-OS/RIOT/blob/2022.10-branch/sys/net/gnrc/network_layer/sixlowpan/iphc/gnrc_sixlowpan_iphc.c#L729
- https://github.com/RIOT-OS/RIOT/blob/2022.10-branch/sys/net/gnrc/network_layer/sixlowpan/iphc/gnrc_sixlowpan_iphc.c#L761
- https://github.com/RIOT-OS/RIOT/blob/ccbb304eae7b59e8aca24a6ffd095b5b3f7720ee/sys/net/gnrc/pktbuf_static/gnrc_pktbuf_static.c#L169
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24825.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-xqm8-xj74-fjw2
- https://nvd.nist.gov/vuln/detail/CVE-2023-24825
- https://github.com/RIOT-OS/RIOT/commit/0c522075445a62ce3102e141573ecc2788521897
