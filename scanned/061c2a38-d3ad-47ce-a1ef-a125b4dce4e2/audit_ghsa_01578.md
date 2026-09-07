# [M] XSS vulnerability when listing users on add & modify server pages.

## Summary
Severity: Medium
Advisory: GHSA-5822-pw57-vv37
CWE: CWE-79
Ecosystem: Packagist
Published: 2020-10-08
Source: https://github.com/advisories/GHSA-5822-pw57-vv37
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <0.7.19
- Packagist: `pterodactyl/panel` — affected >=1.0.0-rc.0 <1.0.0-rc.7

## Details
### Impact
An XSS vulnerability exists in versions of Pterodactyl Panel before 0.7.19. Affected versions do not properly sanitize account names before rendering them to the dropdown selector in the admin area when creating or modifying a server.

### Patches
This XSS has been addressed in 0.7.19 and will be rolled forwards into the 1.0-rc.7 release.

### Workarounds
No workaround exists without manual patching. See https://github.com/pterodactyl/panel/pull/2441/files for the files changed.

### For more information
If you have any questions or comments about this advisory please reach out on Discord, or by emailing `dane` at `pterodactyl` dot `io`.

_Thank you to Sergej for the responsible disclosure of this issue._

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-5822-pw57-vv37
- https://github.com/pterodactyl/panel
