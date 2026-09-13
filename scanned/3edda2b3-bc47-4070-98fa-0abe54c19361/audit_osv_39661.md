# [M] lldpd: Heap OOB Read in VLAN Decapsulation memmove

## Summary
Severity: Medium
Advisory: CVE-2026-46433
Aliases: GHSA-2g8p-2h3j-63m3
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46433
Type: osv

## Details
lldpd is an implementation of IEEE 802.1ab (LLDP). Prior to version 1.0.22, lldpd_decode() in src/daemon/lldpd.c strips 802.1Q VLAN tags from received Ethernet frames by calling memmove() to shift the frame payload 4 bytes left. The third argument (byte count) is s - 2 * ETHER_ADDR_LEN but should be s - 2 * ETHER_ADDR_LEN - 4, causing a 4-byte heap buffer over-read past the malloc(h_mtu) allocation when the received frame size equals the interface MTU. This issue has been patched in version 1.0.22.

## References
- https://github.com/lldpd/lldpd/releases/tag/1.0.22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46433.json
- https://github.com/lldpd/lldpd/security/advisories/GHSA-2g8p-2h3j-63m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46433
- https://github.com/lldpd/lldpd/commit/ca931be63a9cae0fcd8e9b6ae4e916d49f141cd6
- https://github.com/lldpd/lldpd/pull/787
