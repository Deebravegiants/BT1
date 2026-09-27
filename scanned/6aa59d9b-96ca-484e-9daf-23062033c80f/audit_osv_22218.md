# [H] Privilege escalation in Defender

## Summary
Severity: High
Advisory: CVE-2022-23604
Aliases: GHSA-cfh8-v56j-5757
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-23604
Type: osv

## Details
x26-Cogs is a repository of cogs made by Twentysix for the Red Discord bot. Among these cogs is the Defender cog, a tool for Discord server moderation. A vulnerability in the Defender cog prior to version 1.10.0 allows users with admin privileges to issue commands as other users who share the same server. If a bot owner shares the same server as the attacker, it is possible for the attacker to issue bot-owner restricted commands. The issue has been patched in version 1.10.0. One may unload the Defender cog as a workaround.

## References
- https://github.com/Twentysix26/x26-Cogs/releases/tag/v1.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23604.json
- https://github.com/Twentysix26/x26-Cogs/security/advisories/GHSA-cfh8-v56j-5757
- https://nvd.nist.gov/vuln/detail/CVE-2022-23604
- https://github.com/Twentysix26/x26-Cogs/commit/72dd9323cb4c90f3a5accac7087605375d178246
