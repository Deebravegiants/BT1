# [M] CVE-2019-5892

## Summary
Severity: Medium
Advisory: CVE-2019-5892
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/CVE-2019-5892
Type: osv

## Details
bgpd in FRRouting FRR (aka Free Range Routing) 2.x and 3.x before 3.0.4, 4.x before 4.0.1, 5.x before 5.0.2, and 6.x before 6.0.2 (not affecting Cumulus Linux or VyOS), when ENABLE_BGP_VNC is used for Virtual Network Control, allows remote attackers to cause a denial of service (peering session flap) via attribute 255 in a BGP UPDATE packet. This occurred during Disco in January 2019 because FRR does not implement RFC 7606, and therefore the packets with 255 were considered invalid VNC data and the BGP session was closed.

## References
- https://frrouting.org/community/security/cve-2019-5892.html
- https://github.com/FRRouting/frr/releases/tag/frr-3.0.4
- https://github.com/FRRouting/frr/releases/tag/frr-4.0.1
- https://github.com/FRRouting/frr/releases/tag/frr-5.0.2
- https://github.com/FRRouting/frr/releases/tag/frr-6.0.2
- https://github.com/FRRouting/frr/commit/943d595a018e69b550db08cccba1d0778a86705a
- https://lists.frrouting.org/pipermail/frog/2019-January/000404.html
