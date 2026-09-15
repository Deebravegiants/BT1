# [M] Concrete CMS allows unauthorized access because directories can be created with insecure permissions

## Summary
Severity: Medium
Advisory: GHSA-m87h-jxr6-f82w
CVE: CVE-2023-48648
Ecosystem: Packagist
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-m87h-jxr6-f82w
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.13
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.2.2

## Details
Concrete CMS before 8.5.13 and 9.x before 9.2.2 allows unauthorized access because directories can be created with insecure permissions. File creation functions (such as the Mkdir() function) gives universal access (0777) to created folders by default. Excessive permissions can be granted when creating a directory with permissions greater than 0755 or when the permissions argument is not specified.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48648
- https://github.com/concretecms/concretecms/pull/11677
- https://github.com/concretecms/concretecms/commit/707b974826b761dda5c0baaf345c8582157d9307
- https://github.com/concretecms/concretecms/commit/eb882681a0ed19798a8f689d257af8dfe2f3a279
- https://documentation.concretecms.org/developers/introduction/version-history/8513-release-notes
- https://documentation.concretecms.org/developers/introduction/version-history/922-release-notes
- https://github.com/concretecms/concretecms
- https://www.concretecms.org/about/project-news/security/2023-11-09-security-blog-about-updated-cves-and-new-release
