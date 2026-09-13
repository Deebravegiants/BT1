# [M] Improper regex in htaccess file

## Summary
Severity: Medium
Advisory: GHSA-mj6m-246h-9w56
CVE: CVE-2022-25769
Ecosystem: Packagist
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-mj6m-246h-9w56
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <3.3.5
- Packagist: `mautic/core` — affected >=4.0.0 <4.2.0

## Details
### Impact
the default .htaccess file has some restrictions in the access to PHP files to only allow specific PHP files to be executed in the root of the application.

This logic isn't correct, as the regex in the second FilesMatch only checks the filename, not the full path.

### Patches
Please upgrade to 3.3.5 or 4.2.0 

### Workarounds
No

### References

- Release post: https://www.mautic.org/blog/community/mautic-4-2-one-small-step-mautic
- Internally tracked under MST-32

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-mj6m-246h-9w56
