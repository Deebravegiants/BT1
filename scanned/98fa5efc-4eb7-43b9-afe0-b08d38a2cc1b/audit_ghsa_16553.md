# [M] Drupal core Cross-Site Scripting (XSS) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-vfgc-c76h-mwh4
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-vfgc-c76h-mwh4
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.9.18
- Packagist: `drupal/core` — affected >=9.1.0 <9.1.12
- Packagist: `drupal/core` — affected >=9.2.0 <9.2.4

## Details
The Drupal project uses the CKEditor, library for WYSIWYG editing. CKEditor has released a security update that impacts Drupal.

Vulnerabilities are possible if Drupal is configured to allow use of the CKEditor library for WYSIWYG editing. An attacker that can create or edit content (even without access to CKEditor themselves) may be able to exploit one or more Cross-Site Scripting (XSS) vulnerabilities to target users with access to the WYSIWYG CKEditor, including site admins with privileged access.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/2021-05-26.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2021-005
