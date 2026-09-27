# [M] CVE-2021-37697

## Summary
Severity: Medium
Advisory: CVE-2021-37697
Aliases: GHSA-77xv-8c2x-j96j
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/CVE-2021-37697
Type: osv

## Details
tmerc-cogs are a collection of open source plugins for the Red Discord bot. A vulnerability has been found in the code that allows any user to access sensitive information by crafting a specific membership event message. Issue is patched in commit d63c49b4cfc30c795336e4fff08cba3795e0fcc0. As a workaround users may unload the Welcome cog.

## References
- https://github.com/tmercswims/tmerc-cogs/commit/d63c49b4cfc30c795336e4fff08cba3795e0fcc0
- https://github.com/tmercswims/tmerc-cogs/security/advisories/GHSA-77xv-8c2x-j96j
