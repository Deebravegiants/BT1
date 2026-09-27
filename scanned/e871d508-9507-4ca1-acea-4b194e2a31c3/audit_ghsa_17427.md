# [M] JDA (Java Discord API) downloads external URLs when updating message components

## Summary
Severity: Medium
Advisory: GHSA-93fv-4pm9-xp28
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-93fv-4pm9-xp28
Type: github-advisory

## Affected
- Maven: `net.dv8tion:JDA` — affected >=6.0.0 <6.1.3

## Details
### Impact

Anyone using untrusted message components may be affected. On versions >=6.0.0,<6.1.3 of JDA, the requester will attempt to download external media URLs from components if they are used in an update or send request.

If you are used `Message#getComponents` or similar to get a list of components and then send those components with `sendMessageComponents` or other methods, you might unintentionally download media from an external URL in the resolved media of a `Thumbnail`, `FileDisplay`, or `MediaGallery`.

### Patches

This bug has been fixed in 6.1.3, and we recommend updating.

### Workarounds

Avoid sending components from untrusted messages or update to version 6.1.3.

## References
- https://github.com/discord-jda/JDA/security/advisories/GHSA-93fv-4pm9-xp28
- https://github.com/discord-jda/JDA/commit/bb6d2ce5cf514429327c257f5c6fa95a137e3ab6
- https://github.com/discord-jda/JDA
