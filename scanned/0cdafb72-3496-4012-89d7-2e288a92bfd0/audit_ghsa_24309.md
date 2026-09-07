# [M] Drupal improper access restrictions

## Summary
Severity: Medium
Advisory: GHSA-vpm6-h53m-x2xf
CVE: CVE-2012-2153
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vpm6-h53m-x2xf
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=7.0 <7.14

## Details
Drupal 7.x before 7.14 does not properly restrict access to nodes in a list when using a "contributed node access module," which allows remote authenticated users with the "Access the content overview page" permission to read all published nodes by accessing the admin/content page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2153
- https://web.archive.org/web/20150523060428/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2013:074/?name=MDVSA-2013:074
- https://web.archive.org/web/20200229101926/http://www.securityfocus.com/bid/53362
- http://drupal.org/drupal-7.14
- http://drupal.org/node/1557938
- http://drupal.org/node/1558478
- http://drupalcode.org/project/drupal.git/commit/c6d2b8311b82fe78d18732f01a68ceca3dea50af
