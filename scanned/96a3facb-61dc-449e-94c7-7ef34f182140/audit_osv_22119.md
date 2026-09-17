# [C] Bot token exposed in main.py

## Summary
Severity: Critical
Advisory: CVE-2022-21669
Aliases: GHSA-cxgr-xpmj-9qjm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-01-11
Source: https://osv.dev/vulnerability/CVE-2022-21669
Type: osv

## Details
PuddingBot is a group management bot. In version 0.0.6-b933652 and prior, the bot token is publicly exposed in main.py, making it accessible to malicious actors. The bot token has been revoked and new version is already running on the server. As of time of publication, the maintainers are planning to update code to reflect this change at a later date.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21669.json
- https://github.com/PuddingBot/pudding-bot/security/advisories/GHSA-cxgr-xpmj-9qjm
- https://nvd.nist.gov/vuln/detail/CVE-2022-21669
- https://github.com/PuddingBot/pudding-bot/commit/a5b15fb0a5be5fdbacba8ff7b2c8759d5e3ba20f
