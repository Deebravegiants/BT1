# [H] CVE-2021-41191

## Summary
Severity: High
Advisory: CVE-2021-41191
Aliases: GHSA-76mx-6584-4v8q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-27
Source: https://osv.dev/vulnerability/CVE-2021-41191
Type: osv

## Details
Roblox-Purchasing-Hub is an open source Roblox product purchasing hub. A security risk in versions 1.0.1 and prior allowed people who have someone's API URL to get product files without an API key. This issue is fixed in version 1.0.2. As a workaround, add `@require_apikey` in `BOT/lib/cogs/website.py` under the route for `/v1/products`.

## References
- https://github.com/Redon-Tech/Roblox-Purchasing-Hub/releases/tag/V1.0.2
- https://github.com/Redon-Tech/Roblox-Purchasing-Hub/security/advisories/GHSA-76mx-6584-4v8q
- https://github.com/Redon-Tech/Roblox-Purchasing-Hub/commit/58a22260eca40b1a0377daf61ccd8c4dc1440e03
