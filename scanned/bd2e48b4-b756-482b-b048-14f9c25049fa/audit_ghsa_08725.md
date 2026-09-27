# [M] Spatie Laravel Media Library contains a server-side request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fggg-964j-3j7h
CVE: CVE-2026-48555
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-fggg-964j-3j7h
Type: github-advisory

## Affected
- Packagist: `spatie/laravel-medialibrary` — affected >=0 <11.23.0

## Details
Spatie Laravel Media Library before version 11.23.0 contains a server-side request forgery vulnerability that allows remote attackers to cause the server to issue arbitrary outbound HTTP requests by passing user-controlled URLs to the addMediaFromUrl() method in InteractsWithMedia.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48555
- https://github.com/spatie/laravel-medialibrary/pull/3939
- https://github.com/spatie/laravel-medialibrary/commit/608ea03703d3887c46434f5dda6af56de6346aba
- https://github.com/spatie/laravel-medialibrary
- https://github.com/spatie/laravel-medialibrary/releases/tag/11.23.0
- https://www.vulncheck.com/advisories/spatie-laravel-media-library-ssrf-via-addmediafromurl
