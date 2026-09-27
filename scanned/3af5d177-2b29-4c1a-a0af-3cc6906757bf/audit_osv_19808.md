# [H] CVE-2021-25980

## Summary
Severity: High
Advisory: CVE-2021-25980
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-11
Source: https://osv.dev/vulnerability/CVE-2021-25980
Type: osv

## Details
In Talkyard, versions v0.04.01 through v0.6.74-WIP-63220cb, v0.2020.22-WIP-b2e97fe0e through v0.2021.02-WIP-879ef3fe1 and tyse-v0.2021.02-879ef3fe1-regular through tyse-v0.2021.28-af66b6905-regular, are vulnerable to Host Header Injection. By luring a victim application-user to click on a link, an unauthenticated attacker can use the “forgot password” functionality to reset the victim’s password and successfully take over their account.

## References
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25980
- https://github.com/debiki/talkyard/commit/4067e191a909ed06f250d09a40e43aa5edbb0289
