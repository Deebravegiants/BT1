# [C] CVE-2020-14067

## Summary
Severity: Critical
Advisory: CVE-2020-14067
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14067
Type: osv

## Details
The install_from_hash functionality in Navigate CMS 2.9 does not consider the .phtml extension when examining files within a ZIP archive that may contain PHP code, in check_upload in lib/packages/extensions/extension.class.php and lib/packages/themes/theme.class.php.

## References
- https://github.com/NavigateCMS/Navigate-CMS/commit/f1f47126b359d73a2635306ae46d8719c14d240b
