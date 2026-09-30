# [M] BunkerWeb: rDNS bypass via missing forward-confirmation (FCrDNS) in blacklist, greylist, and antibot

## Summary
Severity: Medium
Advisory: CVE-2026-75514
Aliases: GHSA-q54j-5484-pvjm
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-75514
Type: osv

## Details
BunkerWeb is an open-source, next-generation Web Application Firewall. Prior to 1.6.13, the blacklist, greylist, and antibot modules in src/common/core/blacklist/blacklist.lua, src/common/core/greylist/greylist.lua, and src/common/core/antibot/antibot.lua trust PTR suffix matches in IGNORE_RDNS, GREYLIST_RDNS, and ANTIBOT_IGNORE_RDNS without using get_ips to confirm that the hostname resolves to the client address. An unauthenticated remote attacker who controls a PTR record can spoof a trusted suffix to bypass rDNS-based blacklisting, gain greylist treatment, or skip an antibot challenge. This issue is fixed in version 1.6.13.

## References
- https://github.com/bunkerity/bunkerweb/releases/tag/v1.6.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75514.json
- https://github.com/bunkerity/bunkerweb/security/advisories/GHSA-q54j-5484-pvjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-75514
- https://github.com/bunkerity/bunkerweb/commit/1a97e5b3f977130a1b84507a9e1f703c8eec12eb
- https://github.com/bunkerity/bunkerweb/pull/3710
