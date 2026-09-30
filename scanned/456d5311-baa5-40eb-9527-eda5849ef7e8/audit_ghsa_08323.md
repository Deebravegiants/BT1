# [H] elFinder MySQL has a SQL Injection in its Volume Driver (elFinderVolumeMySQL)

## Summary
Severity: High
Advisory: GHSA-c3gj-q88f-7hqj
CVE: CVE-2026-44521
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-c3gj-q88f-7hqj
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.68

## Details
## Summary

An authenticated SQL injection vulnerability in the elFinder MySQL volume driver (`elFinderVolumeMySQL`) allows any logged-in user, including users with read-only access to the affected volume, to inject SQL through a crafted `target` file hash. Successful exploitation can lead to unauthorized data disclosure and denial of service.

This vulnerability only affects installations configured to use the `MySQL` volume driver. Installations using the default `LocalFileSystem` driver are not affected.

## Description

A vulnerability in elFinder's MySQL volume driver (`elFinderVolumeMySQL`) allows authenticated SQL injection through a crafted file hash passed via the `target` parameter.

The issue is caused by two behaviors working together:
1. File hashes are decoded without validating that the decoded value is a valid MySQL object identifier.
2. The decoded value is then used in MySQL driver queries, including `cacheDir()`, `_joinPath()`, `_stat()`, and `_fopen()`.

Because the MySQL storage schema uses numeric `id` and `parent_id` values, an authenticated user can supply a crafted hash that alters the intended SQL query logic. Successful exploitation can lead to unauthorized data disclosure and denial of service. The extent of impact depends on the privileges granted to the configured MySQL account.

This vulnerability only affects installations configured to use the `MySQL` volume driver. Installations using the default `LocalFileSystem` driver are not affected.

## Impact

An authenticated user, including a user with read-only access to the affected volume, can exploit this issue to:
- disclose data accessible to the configured MySQL account, including file contents stored by the driver and database metadata
- trigger denial of service through expensive or unexpectedly broad query results that can lead to excessive memory consumption

The severity of data exposure depends on the privileges granted to the configured MySQL account.

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-c3gj-q88f-7hqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44521
- https://github.com/Studio-42/elFinder
