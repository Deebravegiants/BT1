# [M] Incorrectly Specified Chat Message Destinations in tgstation-server and DreamMaker API

## Summary
Severity: Medium
Advisory: CVE-2023-33198
Aliases: GHSA-p2xj-w57r-6f5m
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33198
Type: osv

## Details
tgstation-server is a production scale tool for BYOND server management. The DreamMaker API (DMAPI) chat channel cache can possibly be poisoned by a tgstation-server (TGS) restart and reattach. This can result in sending chat messages to one of any of the configured IRC or Discord channels for the instance on enabled chat bots. This lasts until the instance's chat channels are updated in TGS or DreamDaemon is restarted. TGS chat commands are unaffected, custom or otherwise.

## References
- https://github.com/tgstation/tgstation-server/releases/tag/tgstation-server-v5.12.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33198.json
- https://github.com/tgstation/tgstation-server/security/advisories/GHSA-p2xj-w57r-6f5m
- https://nvd.nist.gov/vuln/detail/CVE-2023-33198
- https://github.com/tgstation/tgstation-server/pull/1493
