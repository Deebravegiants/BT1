# [C] October CMS safe mode bypass using Twig sandbox escape

## Summary
Severity: Critical
Advisory: GHSA-p8q3-h652-65vx
CVE: CVE-2023-44382
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-p8q3-h652-65vx
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=3.0.0 <3.4.15

## Details
### Impact

An authenticated backend user with the `editor.cms_pages`, `editor.cms_layouts`, or `editor.cms_partials` permissions who would normally not be permitted to provide PHP code to be executed by the CMS due to `cms.safe_mode` being enabled can write specific Twig code to escape the Twig sandbox and execute arbitrary PHP.

This is not a problem for anyone who trusts their users with those permissions to usually write and manage PHP within the CMS by not having `cms.safe_mode` enabled. Still, it would be a problem for anyone relying on `cms.safe_mode` to ensure that users with those permissions in production do not have access to write and execute arbitrary PHP.

### Patches

This issue has been patched in v3.4.15.

### Workarounds

As a workaround, remove the specified permissions from untrusted users.

### References

Credits to:
- [Vasiliy Bodrov](https://github.com/whatev3n)

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-p8q3-h652-65vx
- https://nvd.nist.gov/vuln/detail/CVE-2023-44382
- https://github.com/octobercms/october
