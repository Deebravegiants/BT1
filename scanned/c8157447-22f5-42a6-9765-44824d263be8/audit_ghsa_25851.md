# [H] Old sessions not blocked by login enable function in Snipe-IT

## Summary
Severity: High
Advisory: GHSA-636j-7x7r-gvw2
CVE: CVE-2022-1155
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-636j-7x7r-gvw2
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=6.0.0-RC-1 <6.0.0-RC-6
- Packagist: `snipe/snipe-it` — affected >=0 <5.4.2

## Details
Snipe-IT is a FOSS project for asset management in IT Operations. In Snipe-IT versions 5.4.1 and 6.0.0-RC-5 and prior, active sessions are not revoked when a user account is disabled, allowing that user to still access information that they should no longer be able to. Workarounds include using the KillAllSessions console command, clearing the contents of the storage/framework/sessions directory, or changing the cookie name, but all of those options logout ALL users, which could be kind of annoying. This issue is fixed in versions 6.0.0-RC-6 and 5.4.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1155
- https://github.com/snipe/snipe-it/pull/10876
- https://github.com/snipe/snipe-it/commit/bdabbbd4e98e88ee01e728ceb4fd512661fbd38d
- https://github.com/snipe/snipe-it
- https://github.com/snipe/snipe-it/releases/tag/v5.4.2
- https://github.com/snipe/snipe-it/releases/tag/v6.0.0-RC-6
- https://huntr.dev/bounties/ebc26354-2414-4f72-88aa-f044aec2b2e1
