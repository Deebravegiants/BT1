# [M] Red-DiscordBot vulnerable to Incorrect Authorization in commands API

## Summary
Severity: Medium
Advisory: GHSA-5jq8-q6rj-9gq4
CVE: CVE-2024-39905
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-11
Source: https://github.com/advisories/GHSA-5jq8-q6rj-9gq4
Type: github-advisory

## Affected
- PyPI: `Red-DiscordBot` — affected >=3.5.0 <3.5.10

## Details
### Impact

Due to a bug in Red's Core API, 3rd-party cogs using the [`@commands.can_manage_channel()`](https://docs.discord.red/en/stable/framework_checks.html#redbot.core.commands.can_manage_channel) command permission check without additional permission controls may authorize a user to run a command even when that user doesn't have permissions to manage a channel.
None of the core commands or core cogs are affected. The maintainers of the project are not aware of any _public_ 3rd-party cog utilizing this API at the time of writing this advisory.

The [`@commands.mod_or_can_manage_channel()`](https://docs.discord.red/en/stable/framework_checks.html#redbot.core.commands.mod_or_can_manage_channel), [`@commands.admin_or_can_manage_channel()`](https://docs.discord.red/en/stable/framework_checks.html#redbot.core.commands.admin_or_can_manage_channel), and [`@commands.guildowner_or_can_manage_channel()`](https://docs.discord.red/en/stable/framework_checks.html#redbot.core.commands.guildowner_or_can_manage_channel) command permission checks are unaffected.

CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N
CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N/AU:Y/R:U/RE:L

### Patches

The problem was patched in PR #6398 and later released in version [3.5.10](https://pypi.org/project/Red-DiscordBot/3.5.10/).

### Workarounds

Any cog using the [`@commands.can_manage_channel()`](https://docs.discord.red/en/stable/framework_checks.html#redbot.core.commands.can_manage_channel) command permission check should be unloaded until an upgrade to a patched version can be performed.

### References

https://github.com/Cog-Creators/Red-DiscordBot/pull/6398
https://github.com/Cog-Creators/Red-DiscordBot/releases/tag/3.5.10
https://pypi.org/project/Red-DiscordBot/3.5.10/

## References
- https://github.com/Cog-Creators/Red-DiscordBot/security/advisories/GHSA-5jq8-q6rj-9gq4
- https://nvd.nist.gov/vuln/detail/CVE-2024-39905
- https://github.com/Cog-Creators/Red-DiscordBot/pull/6398
- https://github.com/Cog-Creators/Red-DiscordBot/commit/0b0b23b9717b40ed4f8715720b199417c8e89750
- https://github.com/Cog-Creators/Red-DiscordBot
