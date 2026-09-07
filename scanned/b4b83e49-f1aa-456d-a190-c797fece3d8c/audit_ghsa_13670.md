# [M] October CMS safe mode bypass using Page template injection

## Summary
Severity: Medium
Advisory: GHSA-q22j-5r3g-9hmh
CVE: CVE-2023-44381
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-q22j-5r3g-9hmh
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=3.0.0 <3.4.15

## Details
### Impact

An authenticated backend user with the `editor.cms_pages`, `editor.cms_layouts`, or `editor.cms_partials` permissions who would normally not be permitted to provide PHP code to be executed by the CMS due to `cms.safe_mode` being enabled can craft a special request to include PHP code in the CMS template.

This is not a problem for anyone who trusts their users with those permissions to usually write & manage PHP within the CMS by not having `cms.safe_mode` enabled. Still, it would be a problem for anyone relying on `cms.safe_mode` to ensure that users with those permissions in production do not have access to write and execute arbitrary PHP.

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
- https://github.com/octobercms/october/security/advisories/GHSA-q22j-5r3g-9hmh
- https://nvd.nist.gov/vuln/detail/CVE-2023-44381
- https://github.com/octobercms/october
