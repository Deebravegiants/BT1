# [C] Improper parsing of octal bytes in netmask

## Summary
Severity: Critical
Advisory: GHSA-4c7m-wxvm-r7gc
CVE: CVE-2021-28918
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-14
Source: https://github.com/advisories/GHSA-4c7m-wxvm-r7gc
Type: github-advisory

## Affected
- npm: `netmask` — affected >=0 <1.1.0

## Details
Improper input validation of octal strings in netmask npm package v1.0.6 and below allows unauthenticated remote attackers to perform indeterminate SSRF, RFI, and LFI attacks on many of the dependent packages. A remote unauthenticated attacker can bypass packages relying on netmask to filter IPs and reach critical VPN or LAN hosts.

:exclamation: NOTE: The fix for this issue was incomplete. A subsequent fix was made in version `2.0.1` which was assigned [CVE-2021-29418 / GHSA-pch5-whg9-qr2r](https://github.com/advisories/GHSA-pch5-whg9-qr2r). For complete protection from this vulnerability an upgrade to version 2.0.1 or later is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28918
- https://github.com/advisories/GHSA-pch5-whg9-qr2r
- https://github.com/rs/node-netmask
- https://github.com/rs/node-netmask/blob/98294cb20695f2c6c36219a4fbcd4744fb8d0682/CHANGELOG.md#v110-mar-18-2021
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2021-011.md
- https://rootdaemon.com/2021/03/29/vulnerability-in-netmask-npm-package-affects-280000-projects
- https://security.netapp.com/advisory/ntap-20210528-0010
- https://www.bleepingcomputer.com/news/security/critical-netmask-networking-bug-impacts-thousands-of-applications
- https://www.npmjs.com/package/netmask
