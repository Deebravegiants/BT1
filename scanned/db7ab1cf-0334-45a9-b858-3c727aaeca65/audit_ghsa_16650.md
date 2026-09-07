# [M] Drupal core uses a vulnerable Third-party library CKEditor

## Summary
Severity: Medium
Advisory: GHSA-337w-fxpq-5m34
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-337w-fxpq-5m34
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.7.12
- Packagist: `drupal/drupal` — affected >=8.8.0 <8.8.4

## Details
The Drupal project uses the third-party library [CKEditor](https://github.com/ckeditor/ckeditor4), which has released a [security improvement](https://ckeditor.com/blog/CKEditor-4.14-with-Paste-from-LibreOffice-released/#security-issues-fixed) that is needed to protect some Drupal configurations.

Vulnerabilities are possible if Drupal is configured to use the WYSIWYG CKEditor for your site's users. An attacker that can create or edit content may be able to exploit this Cross Site Scripting (XSS) vulnerability to target users with access to the WYSIWYG CKEditor, and this may include site admins with privileged access.

The latest versions of Drupal update CKEditor to 4.14 to mitigate the vulnerabilities.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/2020-03-18.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/sa-core-2020-001
