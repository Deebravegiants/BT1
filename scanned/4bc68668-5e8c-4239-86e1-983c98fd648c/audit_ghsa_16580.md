# [M] Drupal Malicious file upload with filenames stating with dot

## Summary
Severity: Medium
Advisory: GHSA-58xv-7h9r-mx3c
CWE: CWE-434
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-58xv-7h9r-mx3c
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.7.11
- Packagist: `drupal/drupal` — affected >=8.8.0 <8.8.1

## Details
Drupal 8 core's file_save_upload() function does not strip the leading and trailing dot ('.') from filenames, like Drupal 7 did.

Users with the ability to upload files with any extension in conjunction with contributed modules may be able to use this to upload system files such as .htaccess in order to bypass protections afforded by Drupal's default .htaccess file.

After this fix, file_save_upload() now trims leading and trailing dots from filenames.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/2019-12-18-2.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/sa-core-2019-010
