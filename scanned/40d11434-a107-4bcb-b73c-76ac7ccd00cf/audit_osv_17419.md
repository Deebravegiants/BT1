# [C] CVE-2020-15140

## Summary
Severity: Critical
Advisory: CVE-2020-15140
Aliases: GHSA-55j9-849x-26h4, PYSEC-2020-265
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-15140
Type: osv

## Details
In Red Discord Bot before version 3.3.11, a RCE exploit has been discovered in the Trivia module: this exploit allows Discord users with specifically crafted usernames to inject code into the Trivia module's leaderboard command. By abusing this exploit, it's possible to perform destructive actions and/or access sensitive information. This critical exploit has been fixed on version 3.3.11.

## References
- https://github.com/Cog-Creators/Red-DiscordBot/security/advisories/GHSA-55j9-849x-26h4
- https://github.com/Cog-Creators/Red-DiscordBot/pull/4175/commits/9ab536235bafc2b42c3c17d7ce26f1cc64482a81
