# [M] Silverstripe Assets Module has a DBFile::getURL() permission bypass

## Summary
Severity: Medium
Advisory: GHSA-jgcf-rf45-2f8v
CVE: CVE-2026-24749
CWE: CWE-266, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-jgcf-rf45-2f8v
Type: github-advisory

## Affected
- Packagist: `silverstripe/assets` — affected >=0 <2.4.5
- Packagist: `silverstripe/assets` — affected >=3.0.0 <3.1.3

## Details
### Impact

Images rendered in templates or otherwise accessed via `DBFile::getURL()` or `DBFile::getSourceURL()` incorrectly add an access grant to the current session, which bypasses file permissions.

This usually happens when creating an image variant, for example using a manipulation method like `ScaleWidth()` or `Convert()`.

Note that if you use `DBFile` directly in the `$db` configuration for a `DataObject` class that doesn't subclass `File`, and if you were setting the visibility of those files to "protected", those files will now need an explicit access grant to be accessed. If you do not want to explicitly provide access grants for these files (i.e. you want these files to be accessible by default), you should use the "public" visibility.

### Reported by

Restruct web & apps

## References
- https://github.com/silverstripe/silverstripe-assets/security/advisories/GHSA-jgcf-rf45-2f8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-24749
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/assets/CVE-2026-24749.yaml
- https://github.com/silverstripe/silverstripe-assets
- https://www.silverstripe.org/download/security-releases/cve-2026-24749
