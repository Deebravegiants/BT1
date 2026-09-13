# [M] Camaleon CMS vulnerable to Path Traversal through AWS S3 uploader implementation

## Summary
Severity: Medium
Advisory: GHSA-jw5g-f64p-6x78
CVE: CVE-2026-1776
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-jw5g-f64p-6x78
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=2.4.5.0

## Details
Camaleon CMS versions 2.4.5.0 through 2.9.1, prior to commit f54a77e, contain a path traversal vulnerability in the AWS S3 uploader implementation that allows authenticated users to read arbitrary files from the web server’s filesystem. The issue occurs in the download_private_file functionality when the application is configured to use the CamaleonCmsAwsUploader backend. Unlike the local uploader implementation, the AWS uploader does not validate file paths with valid_folder_path?, allowing directory traversal sequences to be supplied via the file parameter. As a result, any authenticated user, including low-privileged registered users, can access sensitive files such as /etc/passwd. This issue represents a bypass of the incomplete fix for CVE-2024-46987 and affects deployments using the AWS S3 storage backend.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1776
- https://github.com/owen2345/camaleon-cms/pull/1127
- https://github.com/owen2345/camaleon-cms/commit/f54a77e2a7be601215ea1b396038c589a0cab9af
- https://camaleon.website
- https://github.com/owen2345/camaleon-cms
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2026-1776.yml
- https://www.vulncheck.com/advisories/camaleon-cms-aws-uploader-authenticated-path-traversal-arbitrary-file-read
