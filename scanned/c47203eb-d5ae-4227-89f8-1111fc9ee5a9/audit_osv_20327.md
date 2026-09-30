# [M] CVE-2021-32795

## Summary
Severity: Medium
Advisory: CVE-2021-32795
Aliases: GHSA-5v34-4prm-9474
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2021-32795
Type: osv

## Details
ArchiSteamFarm is a C# application with primary purpose of idling Steam cards from multiple accounts simultaneously. In versions prior to 4.3.1.0 a Denial of Service (aka DoS) vulnerability which allows attacker to remotely crash running ASF instance through sending a specifically-crafted Steam chat message exists. The user sending the message does not need to be authorized within the bot or ASF process. The attacker needs to know ASF's `CommandPrefix` in advance, but majority of ASF setups run with an unchanged default value. This attack does not allow attacker to gain any potentially-sensitive information, such as logins or passwords, does not allow to execute arbitrary commands and otherwise exploit the crash further. The issue is patched in ASF V4.3.1.0. The only workaround which guarantees complete protection is running all bots with `OnlineStatus` of `0` (Offline). In this setup, ASF is able to ignore even the specifically-crafted message without attempting to interpret it.

## References
- https://github.com/JustArchiNET/ArchiSteamFarm/commit/4cd581ec041912cf199c5512fe6d1dcaec0594c0
- https://github.com/JustArchiNET/ArchiSteamFarm/security/advisories/GHSA-5v34-4prm-9474
- https://steamcommunity.com/groups/archiasf/discussions/1/2935742047969570844/
