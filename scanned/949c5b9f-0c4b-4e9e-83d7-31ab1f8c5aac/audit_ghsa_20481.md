# [M] Book page text, count, and author/title length is not limited in PocketMine-MP

## Summary
Severity: Medium
Advisory: GHSA-p62j-hrxm-xcxf
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-p62j-hrxm-xcxf
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <3.26.5
- Packagist: `pocketmine/pocketmine-mp` — affected >=4.0.0 <4.0.5

## Details
### Impact
Players can fill book pages with as many characters as they like; the server does not check this.
In addition, the maximum of 50 pages is also not enforced, meaning that players can create "book bombs".

This causes a variety of problems:
- Oversized NBT on the wire costing excess bandwidth for server and client
- Server crashes when saving region-based worlds due to exceeding maximum chunk size of 1 MB (PM3-specific)
- Server crashes if any book page exceeds 32 KiB (due to TAG_String size limit) (PM4-specific)

This does, however, require that an attacker obtain a writable book in the first place in order to exploit the problem.

### Patches
The bug has been fixed in 3.26.5 and 4.0.5.

### Workarounds
Ban writable books, or use a plugin to cancel `PlayerEditBookEvent` to cancel the event if `strlen(text) > 1024 || mb_strlen(text) > 256`.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-p62j-hrxm-xcxf
- https://github.com/pmmp/PocketMine-MP
