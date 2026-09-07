# [H] Drupal core Information Disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-xh3v-6f9j-wxw3
CVE: CVE-2022-25275
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-xh3v-6f9j-wxw3
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0.0 <7.91
- Packagist: `drupal/core` — affected >=8.0.0 <9.3.19
- Packagist: `drupal/core` — affected >=9.4.0 <9.4.3

## Details
In some situations, the Image module does not correctly check access to image files not stored in the standard public files directory when generating derivative images using the image styles system.

Access to a non-public file is checked only if it is stored in the "private" file system. However, some contributed modules provide additional file systems, or schemes, which may lead to this vulnerability.

This vulnerability is mitigated by the fact that it only applies when the site sets (Drupal 9) `$config['image.settings']['allow_insecure_derivatives']` or (Drupal 7) `$conf['image_allow_insecure_derivatives']` to TRUE. The recommended and default setting is FALSE, and Drupal core does not provide a way to change that in the admin UI.

Some sites may require configuration changes following this security release. Review the release notes for your Drupal version if you have issues accessing files or image styles after updating.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25275
- https://github.com/drupal/core/commit/2d5f47fc8a166115f56c2330a81e83abe22445cf
- https://github.com/drupal/core/commit/e2fbf63700819cb470a1be425798f1a3f2020116
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2022-25275.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2022-012
