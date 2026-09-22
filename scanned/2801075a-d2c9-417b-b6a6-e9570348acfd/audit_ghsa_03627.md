# [H] Unrestricted file uploads in Contao

## Summary
Severity: High
Advisory: GHSA-wjx8-cgrm-hh8p
CVE: CVE-2019-19745
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-12-17
Source: https://github.com/advisories/GHSA-wjx8-cgrm-hh8p
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.46
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.8.6
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.46
- Packagist: `contao/contao` — affected >=4.5.0 <4.8.6

## Details
### Impact

A back end user with access to the form generator can upload arbitrary files and execute them on the server.

### Patches

Update to Contao 4.4.46 or 4.8.6.

### Workarounds

Configure your web server so it does not execute PHP files and other scripts in the Contao file upload directory.

### References

https://contao.org/en/security-advisories/unrestricted-file-uploads

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-wjx8-cgrm-hh8p
- https://nvd.nist.gov/vuln/detail/CVE-2019-19745
- https://contao.org/en/news.html
- https://contao.org/en/security-advisories/unrestricted-file-uploads.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2019-19745.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2019-19745.yaml
- https://github.com/contao/contao
