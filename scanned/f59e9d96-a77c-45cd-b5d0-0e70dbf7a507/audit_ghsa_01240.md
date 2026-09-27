# [M] Contao Insert tag injection in forms

## Summary
Severity: Medium
Advisory: GHSA-f7wm-x4gw-6m23
CVE: CVE-2020-25768
CWE: CWE-20, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-09-24
Source: https://github.com/advisories/GHSA-f7wm-x4gw-6m23
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.52
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.9.6
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.52
- Packagist: `contao/contao` — affected >=4.5.0 <4.9.6
- Packagist: `contao/contao` — affected >=4.10.0 <4.10.1
- Packagist: `contao/core-bundle` — affected >=4.10.0 <4.10.1

## Details
### Impact

It is possible to inject insert tags in front end forms which will be replaced when the page is rendered.

### Patches

Update to Contao 4.4.52, 4.9.6 or 4.10.1.

### Workarounds

Disable the front end login form and do not use form fields with array keys such as `fieldname[]`.

### References

https://contao.org/en/security-advisories/insert-tag-injection-in-forms

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-f7wm-x4gw-6m23
- https://nvd.nist.gov/vuln/detail/CVE-2020-25768
- https://community.contao.org/en/forumdisplay.php?4-Announcements
- https://contao.org/en/security-advisories/insert-tag-injection-in-forms.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2020-25768.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2020-25768.yaml
- https://github.com/contao/contao
