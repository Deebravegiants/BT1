# [H] Drupal core Multiple vulnerabilities due to the use of the third-party library Archive_Tar

## Summary
Severity: High
Advisory: GHSA-m9fv-whq2-6wmc
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-m9fv-whq2-6wmc
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.69
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.7.11
- Packagist: `drupal/drupal` — affected >=8.8.0 <8.8.1

## Details
The Drupal project uses the third-party library [Archive_Tar](https://pear.php.net/package/Archive_Tar/), which has released a security improvement that is needed to protect some Drupal configurations.

Multiple vulnerabilities are possible if Drupal is configured to allow .tar, .tar.gz, .bz2 or .tlz file uploads and processes them.

The latest versions of Drupal update Archive_Tar to 1.4.9 to mitigate the file processing vulnerabilities.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/2019-12-18-4.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/sa-core-2019-012
