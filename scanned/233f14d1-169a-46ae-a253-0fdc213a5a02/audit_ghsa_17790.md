# [H] Property reflection in System.Linq.Dynamic.Core

## Summary
Severity: High
Advisory: GHSA-4cv2-4hjh-77rx
CVE: CVE-2024-51417
Ecosystem: NuGet
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-4cv2-4hjh-77rx
Type: github-advisory

## Affected
- NuGet: `System.Linq.Dynamic.Core` — affected >=0 <1.6.0

## Details
An issue in System.Linq.Dynamic.Core versions before v.1.6.0 allow remote access to properties on reflection types and static properties/fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51417
- https://github.com/zzzprojects/System.Linq.Dynamic.Core/issues/867
- https://github.com/zzzprojects/System.Linq.Dynamic.Core/commit/49b6cf0909cf3571e0d3580317675408300dbdac
- https://dynamic-linq.net/expression-language#operators
- https://github.com/zzzprojects/System.Linq.Dynamic.Core
- https://zzzprojects.com
