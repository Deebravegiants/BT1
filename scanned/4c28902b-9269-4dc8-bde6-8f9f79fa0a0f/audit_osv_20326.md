# [H] CVE-2021-32794

## Summary
Severity: High
Advisory: CVE-2021-32794
Aliases: GHSA-wxx4-66c2-vj2v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2021-32794
Type: osv

## Details
ArchiSteamFarm is a C# application with primary purpose of idling Steam cards from multiple accounts simultaneously. Due to a bug in ASF code `POST /Api/ASF` ASF API endpoint responsible for updating global ASF config incorrectly removed `IPCPassword` from the resulting config when the caller did not specify it explicitly. Due to the above, it was possible for the user to accidentally remove `IPCPassword` security measure from his IPC interface when updating global ASF config, which exists as part of global config update functionality in ASF-ui. Removal of `IPCPassword` possesses a security risk, as unauthorized users may in result access the IPC interface after such modification. The issue is patched in ASF V5.1.2.4 and future versions. We recommend to manually verify that `IPCPassword` is specified after update, and if not, set it accordingly. In default settings, ASF is configured to allow IPC access from `localhost` only and should not affect majority of users.

## References
- https://github.com/JustArchiNET/ArchiSteamFarm/pull/2379
- https://github.com/JustArchiNET/ArchiSteamFarm/security/advisories/GHSA-wxx4-66c2-vj2v
- https://steamcommunity.com/groups/archiasf/discussions/6/3057365873428498659/
