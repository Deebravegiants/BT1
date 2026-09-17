# [M] CVE-2021-37696

## Summary
Severity: Medium
Advisory: CVE-2021-37696
Aliases: GHSA-ffhm-9c8j-wx9h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/CVE-2021-37696
Type: osv

## Details
tmerc-cogs are a collection of open source plugins for the Red Discord bot. A vulnerability has been found in the code that allows any user to access sensitive information by crafting a specific MassDM message. Issue is patched in commit 92325be650a6c17940cc52611797533ed95dbbe1. All users are advised to update to the current commit. As a workaround users may unload the MassDM cog or globally disable the `[p]massdm` command.

## References
- https://github.com/tmercswims/tmerc-cogs/commit/92325be650a6c17940cc5
- https://github.com/tmercswims/tmerc-cogs/security/advisories/GHSA-ffhm-9c8j-wx9h
