# [H] Laravel-Mediable: path traversal vulnerability in the File::sanitizePath()

## Summary
Severity: High
Advisory: GHSA-xv8g-76mx-2rxc
CVE: CVE-2026-49970
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-xv8g-76mx-2rxc
Type: github-advisory

## Affected
- Packagist: `plank/laravel-mediable` — affected >=0 <7.0.0

## Details
Laravel-Mediable before 7.0.0 contains a path traversal vulnerability in the File::sanitizePath() function that allows attackers to write uploaded files to arbitrary locations by controlling the directory argument passed to MediaUploader::toDestination(). Attackers can exploit the permissive character-class regex that allows both dot and slash characters combined with an ineffective trailing trim() call to bypass sanitization and upload files to sensitive locations such as the document root, environment configuration files, or application configuration directories, enabling remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49970
- https://github.com/plank/laravel-mediable/pull/391
- https://github.com/plank/laravel-mediable/commit/6d1e7fb39922fdfb3b2d120e13f4eb2e653ae082
- https://github.com/plank/laravel-mediable
- https://github.com/plank/laravel-mediable/releases/tag/7.0.0
- https://www.vulncheck.com/advisories/laravel-mediable-path-traversal-via-file-sanitizepath
