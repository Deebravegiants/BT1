# [H] SudoBot missing authorization check in `-config` command

## Summary
Severity: High
Advisory: CVE-2024-45307
Aliases: GHSA-crgg-w3rr-r9h4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-45307
Type: osv

## Details
SudoBot, a Discord moderation bot, is vulnerable to privilege escalation and exploit of the `-config` command in versions prior to 9.26.7. Anyone is theoretically able to update any configuration of the bot and potentially gain control over the bot's settings. Every version of v9 before v9.26.7 is affected. Other versions (e.g. v8) are not affected. Users should upgrade to version 9.26.7 to receive a patch. A workaround would be to create a command permission overwrite in the Database. A SQL statement provided in the GitHub Security Advisor can be executed to create a overwrite that disallows users without `ManageGuild` permission to run the `-config` command. Run the SQL statement for every server the bot is in, and replace `<guild_id>` with the appropriate Guild ID each time.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45307.json
- https://github.com/onesoft-sudo/sudobot/security/advisories/GHSA-crgg-w3rr-r9h4
- https://nvd.nist.gov/vuln/detail/CVE-2024-45307
- https://github.com/onesoft-sudo/sudobot/commit/ef46ca98562f3c1abef4ff7dd94d8f7b8155ee50
