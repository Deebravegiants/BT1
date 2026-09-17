# [M] Tandoor Recipes: WebP and GIF Image Uploads Bypass EXIF/Metadata Stripping, Leaking GPS Coordinates and PII

## Summary
Severity: Medium
Advisory: CVE-2026-29055
Aliases: GHSA-9g2j-xccg-9mhq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-29055
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. In versions prior to 2.6.0, the image processing pipeline in Tandoor Recipes explicitly skips EXIF metadata stripping, image rescaling, and size validation for WebP and GIF image formats. A developer TODO comment in the source code acknowledges this as a known issue. As a result, when users upload recipe photos in WebP format (the default format for modern smartphone cameras), their sensitive EXIF data — including GPS coordinates, camera model, timestamps, and software information — is stored and served to all users who can view the recipe. Version 2.6.0 fixes the issue.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29055.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-9g2j-xccg-9mhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-29055
