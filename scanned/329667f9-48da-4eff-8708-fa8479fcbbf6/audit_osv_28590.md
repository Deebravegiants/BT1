# [M] paperless-ngx's remote user auth via header works even when disabling it for API

## Summary
Severity: Medium
Advisory: CVE-2024-35184
Aliases: GHSA-72w4-hxqq-c256
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-05-15
Source: https://osv.dev/vulnerability/CVE-2024-35184
Type: osv

## Details
Paperless-ngx is a document management system that transforms physical documents into a searchable online archive. Starting in version 2.5.0 and prior to version 2.8.6, remote user authentication allows API access even if API access is explicitly disabled. Version 2.8.6 contains a patchc for the issue.

## References
- https://github.com/paperless-ngx/paperless-ngx/releases/tag/v2.8.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35184.json
- https://github.com/paperless-ngx/paperless-ngx/security/advisories/GHSA-72w4-hxqq-c256
- https://nvd.nist.gov/vuln/detail/CVE-2024-35184
- https://github.com/paperless-ngx/paperless-ngx/commit/ed05b40ba461641b1b59b0a92f51f3f6a66ce180
- https://github.com/paperless-ngx/paperless-ngx/pull/6739
