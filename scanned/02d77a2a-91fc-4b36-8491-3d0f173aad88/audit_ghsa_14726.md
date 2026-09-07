# [M] TunnelVision - decloaking VPNs using DHCP

## Summary
Severity: Medium
Advisory: GHSA-hqmp-g7ph-x543
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-27
Source: https://github.com/advisories/GHSA-hqmp-g7ph-x543
Type: github-advisory

## Affected
- crates.io: `quincy` — affected >=0

## Details
A new decloaking technique for nearly all VPN implementations has been found, which allows attackers to inject entries into the routing tables of unsuspecting victims using DHCP option 121. This allows attackers to redirect traffic, which is supposed to be sent encrypted over the VPN, through the physical interface handling DHCP for the network the victim's computer is connected to, effectively bypassing the VPN connection.

### Impact
All users are potentially affected, as this attack vector can be used against _any_ VPN implementation without mitigations in place.

### Patches
Currently, there are no existing mitigations employed by Quincy.

### Workarounds
Disabling DHCP option 121 in the DHCP client is a potential workaround, as it prevents this kind of attack.

### References
https://www.leviathansecurity.com/blog/tunnelvision

## References
- https://github.com/M0dEx/quincy/security/advisories/GHSA-hqmp-g7ph-x543
- https://nvd.nist.gov/vuln/detail/CVE-2024-3661
- https://github.com/M0dEx/quincy
- https://www.leviathansecurity.com/blog/tunnelvision
