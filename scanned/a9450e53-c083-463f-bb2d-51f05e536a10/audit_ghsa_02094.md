# [H] XSS in Mautic

## Summary
Severity: High
Advisory: GHSA-p7v4-gm6j-cw9m
CVE: CVE-2021-3142
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-p7v4-gm6j-cw9m
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=3.0.0 <3.2.4
- Packagist: `mautic/core` — affected >=2.0.0 <2.16.5

## Details
### Impact
This is a cross-site scripting vulnerability relating to creating/editing a company which requires the user to be logged in as an administrator to be executed.

This vulnerability was reported by Dardan Prebreza at Bishop Fox.

### Patches
Upgrade to 3.2.4 or 2.16.5.

Link to patch for 2.x versions: https://github.com/mautic/mautic/compare/2.16.4...2.16.5.diff

Link to patch for 3.x versions: https://github.com/mautic/mautic/compare/3.2.2...3.2.4.diff

### Workarounds
None

### References
https://www.mautic.org/blog/community/security-release-all-versions-mautic-prior-2-16-5-and-3-2-4

### For more information
If you have any questions or comments about this advisory:
* Post in https://forum.mautic.org/c/support
* Email us at security@mautic.org

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-p7v4-gm6j-cw9m
- https://nvd.nist.gov/vuln/detail/CVE-2021-3142
- https://github.com/mautic/mautic/commit/ba31db23e664f889da55a29ff27f797e2ab5cb1b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2021-3142.yaml
- https://github.com/mautic/mautic/releases/tag/3.2.4
- https://www.mautic.org/blog/community/security-release-all-versions-mautic-prior-2-16-5-and-3-2-3
- https://www.mautic.org/blog/community/security-release-all-versions-mautic-prior-2-16-5-and-3-2-4
