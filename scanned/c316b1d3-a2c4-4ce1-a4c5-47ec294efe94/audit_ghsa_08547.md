# [H] Spatie Laravel Media Library contains a file upload restriction bypass

## Summary
Severity: High
Advisory: GHSA-3ggm-c5m7-hfv5
CVE: CVE-2026-48557
CWE: CWE-184
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-3ggm-c5m7-hfv5
Type: github-advisory

## Affected
- Packagist: `spatie/laravel-medialibrary` — affected >=0 <11.23.0

## Details
Spatie Laravel Media Library before version 11.23.0 contains a file upload restriction bypass in FileAdder::defaultSanitizer(). The sanitizer checks only the final filename suffix, allowing double-extension filenames such as shell.php.jpg to bypass the blocklist, with pathinfo() preserving inner .php stems in saved filenames. The blocklist also omits executable extensions including .php6, .shtml, and .htaccess. The double-extension bypass requires a legacy Apache AddHandler configuration to achieve PHP execution; the incomplete blocklist bypass does not.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48557
- https://github.com/spatie/laravel-medialibrary/pull/3939
- https://github.com/spatie/laravel-medialibrary/commit/608ea03703d3887c46434f5dda6af56de6346aba
- https://github.com/spatie/laravel-medialibrary
- https://github.com/spatie/laravel-medialibrary/releases/tag/11.23.0
- https://www.vulncheck.com/advisories/spatie-laravel-media-library-file-upload-restriction-bypass-via-fileadder-php
