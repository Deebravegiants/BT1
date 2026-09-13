# [H] CVE-2021-29493

## Summary
Severity: High
Advisory: CVE-2021-29493
Aliases: GHSA-f4j2-2cwr-h473
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-29493
Type: osv

## Details
Kennnyshiwa-cogs contains cogs for Red Discordbot. An RCE exploit has been found in the Tickets module of kennnyshiwa-cogs. This exploit allows discord users to craft a message that can reveal sensitive and harmful information. Users can upgrade to version 5a84d60018468e5c0346f7ee74b2b4650a6dade7 to receive a patch or, as a workaround, unload tickets to render the exploit unusable.

## References
- https://github.com/kennnyshiwa/kennnyshiwa-cogs/commit/5a84d60018468e5c0346f7ee74b2b4650a6dade7
- https://github.com/kennnyshiwa/kennnyshiwa-cogs/security/advisories/GHSA-f4j2-2cwr-h473
