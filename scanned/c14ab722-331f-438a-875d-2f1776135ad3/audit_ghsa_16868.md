# [H] Mautic vulnerable to Relative Path Traversal / Arbitrary File Deletion due to GrapesJS builder

## Summary
Severity: High
Advisory: GHSA-9fcx-cv56-w58p
CVE: CVE-2021-27916
CWE: CWE-22, CWE-23
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-9fcx-cv56-w58p
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=3.3.0 <4.4.12
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.0.4

## Details
### Impact
Prior to the patched version, logged in users of Mautic are vulnerable to Relative Path Traversal/Arbitrary File Deletion.  Regardless of the level of access the Mautic user had, they could delete files other than those in the media folders such as system files, libraries or other important files.

This vulnerability exists in the implementation of the GrapesJS builder in Mautic.

### Patches
Update to 4.4.12 or 5.0.4.

### Workarounds
No

### References
- https://cwe.mitre.org/data/definitions/23.html
- https://cwe.mitre.org/data/definitions/22.html
- https://attack.mitre.org/techniques/T1630/002/

### For more information

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-9fcx-cv56-w58p
- https://nvd.nist.gov/vuln/detail/CVE-2021-27916
- https://github.com/mautic/mautic/commit/546045ff9c74dd8b3dac36c4ab3674380262c65a
- https://github.com/mautic/mautic/commit/95e8df3ae6730c725f1848d70e7992da369518f3
- https://github.com/mautic/mautic
