# [C] XSS vulnerability leveraged through referrers could allow un-authorized admin access in Mautic

## Summary
Severity: Critical
Advisory: GHSA-39wj-j3jc-858m
CVE: CVE-2020-35124
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-39wj-j3jc-858m
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=3.0.0 <3.2.4
- Packagist: `mautic/core` — affected >=2.0.0 <2.16.5

## Details
### Impact
This is a cross-site scripting vulnerability which affects every version of Mautic and could allow an attacker unauthorised administrator level access to Mautic.

This vulnerability was reported by Naveen Sunkavally at Horizon3.ai.

### Patches
Upgrade to 3.2.4 or 2.16.5.

Link to patch for 2.x versions: https://github.com/mautic/mautic/compare/2.16.4...2.16.5.diff

Link to patch for 3.x versions: https://github.com/mautic/mautic/compare/3.2.2...3.2.4.diff

### Workarounds
None

### For more information
If you have any questions or comments about this advisory:
* Post in https://forum.mautic.org/c/support
* Email us at security@mautic.org

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-39wj-j3jc-858m
- https://nvd.nist.gov/vuln/detail/CVE-2020-35124
- https://github.com/mautic/mautic/commit/20c5dc39b62164f6922ce53ea42cbb4ccec64e57
- https://forum.mautic.org/c/announcements/16
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2020-35124.yaml
- https://packagist.org/packages/mautic/core
- https://www.horizon3.ai/disclosures/mautic-unauth-xss-to-rce
- https://www.mautic.org/blog/community/security-release-all-versions-mautic-prior-2-16-5-and-3-2-4
