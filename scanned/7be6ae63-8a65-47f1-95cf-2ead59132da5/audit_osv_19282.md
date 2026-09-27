# [C] CVE-2020-9757

## Summary
Severity: Critical
Advisory: CVE-2020-9757
Aliases: GHSA-6q4j-8pjm-5mgc
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-04
Source: https://osv.dev/vulnerability/CVE-2020-9757
Type: osv

## Details
The SEOmatic component before 3.3.0 for Craft CMS allows Server-Side Template Injection that leads to RCE via malformed data to the metacontainers controller.

## References
- https://github.com/nystudio107/craft-seomatic/blob/v3/CHANGELOG.md
- https://github.com/nystudio107/craft-seomatic/commit/65ab659cb6c914c7ad671af1e417c0da2431f79b
- https://github.com/nystudio107/craft-seomatic/commit/a1c2cad7e126132d2442ec8ec8e9ab43df02cc0f
- https://github.com/giany/CVE/blob/master/CVE-2020-9757.txt
