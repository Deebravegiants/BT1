# [M] PHP file inclusion via insert tags

## Summary
Severity: Medium
Advisory: GHSA-r6mv-ppjc-4hgr
CVE: CVE-2021-37626
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-r6mv-ppjc-4hgr
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.56
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.9.18
- Packagist: `contao/core-bundle` — affected >=4.10.0 <4.11.7
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.56
- Packagist: `contao/contao` — affected >=4.5.0 <4.9.18
- Packagist: `contao/contao` — affected >=4.10.0 <4.11.7

## Details
### Impact

It is possible for untrusted users to load arbitrary PHP files via insert tags.

Installations are only affected if there are untrusted back end users.

### Patches

Update to Contao 4.4.56, 4.9.18 or 4.11.7.

### Workarounds

Disable the login for untrusted back end users.

### References

https://contao.org/en/security-advisories/php-file-inclusion-via-insert-tags

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-r6mv-ppjc-4hgr
- https://nvd.nist.gov/vuln/detail/CVE-2021-37626
- https://contao.org/en/security-advisories/php-file-inclusion-via-insert-tags.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2021-37626.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2021-37626.yaml
- https://github.com/contao/contao
