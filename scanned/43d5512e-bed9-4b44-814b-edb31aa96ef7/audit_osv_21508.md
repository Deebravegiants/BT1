# [C] CVE-2021-43617

## Summary
Severity: Critical
Advisory: CVE-2021-43617
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-14
Source: https://osv.dev/vulnerability/CVE-2021-43617
Type: osv

## Details
Laravel Framework through 8.70.2 does not sufficiently block the upload of executable PHP content because Illuminate/Validation/Concerns/ValidatesAttributes.php lacks a check for .phar files, which are handled as application/x-httpd-php on systems based on Debian. NOTE: this CVE Record is for Laravel Framework, and is unrelated to any reports concerning incorrectly written user applications for image upload.

## References
- https://github.com/laravel/framework/blob/2049de73aa099a113a287587df4cc522c90961f5/src/Illuminate/Validation/Concerns/ValidatesAttributes.php#L1331-L1333
- https://salsa.debian.org/php-team/php/-/blob/dc253886b5b2e9bc8d9e36db787abb083a667fd8/debian/php-cgi.conf#L5-6
- https://salsa.debian.org/php-team/php/-/commit/dc253886b5b2e9bc8d9e36db787abb083a667fd8
