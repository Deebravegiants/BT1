# [M] pimcore/admin-ui-classic-bundle Cross-site Scripting vulnerability in Translations

## Summary
Severity: Medium
Advisory: GHSA-m988-7375-7g2c
CVE: CVE-2023-42817
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-m988-7375-7g2c
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.1.2

## Details
### Impact
The translation value with text including “%s” (from “%suggest%) is parsed by sprintf() even though it’s supposed to be output literally to the user.

The translations may be accessible by a user with comparatively lower overall access (as the translation permission cannot be scoped to certain “modules”) and a skilled attacker might be able to exploit the parsing of the translation string in the dialog box.

### Patches
https://github.com/pimcore/admin-ui-classic-bundle/commit/abd7739298f974319e3cac3fd4fcd7f995b63e4c.patch

### Workarounds
Update to version 1.1.2 or apply this patches manually
https://github.com/pimcore/admin-ui-classic-bundle/commit/abd7739298f974319e3cac3fd4fcd7f995b63e4c.patch

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-m988-7375-7g2c
- https://nvd.nist.gov/vuln/detail/CVE-2023-42817
- https://github.com/pimcore/admin-ui-classic-bundle/commit/abd7739298f974319e3cac3fd4fcd7f995b63e4c
- https://github.com/pimcore/admin-ui-classic-bundle
