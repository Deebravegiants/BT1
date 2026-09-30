# [H] Path traversal vulnerability in the file manager

## Summary
Severity: High
Advisory: GHSA-fp7q-xhhw-6rj3
CVE: CVE-2023-29200
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-fp7q-xhhw-6rj3
Type: github-advisory

## Affected
- Packagist: `contao/contao` — affected >=4.9.0 <4.9.40
- Packagist: `contao/contao` — affected >=4.13.0 <4.13.21
- Packagist: `contao/contao` — affected >=5.1.0 <5.1.4

## Details
### Impact

Authenticated users in the back end can list files outside the document root in the file manager.

### Patches

Update to Contao 4.9.40, 4.13.21 or 5.1.4.

### Workarounds

None.

### References

https://contao.org/en/security-advisories/directory-traversal-in-the-file-manager

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-fp7q-xhhw-6rj3
- https://nvd.nist.gov/vuln/detail/CVE-2023-29200
- https://github.com/contao/contao/commit/6f3e705f4ff23f4419563d09d8485793569f31df
- https://contao.org/en/security-advisories/directory-traversal-in-the-file-manager
- https://contao.org/en/security-advisories/directory-traversal-in-the-file-manager.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2023-29200.yaml
- https://github.com/contao/contao
