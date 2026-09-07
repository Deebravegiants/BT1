# [M] Cross-site Scripting in enshrined/svg-sanitize

## Summary
Severity: Medium
Advisory: GHSA-fqx8-v33p-4qcc
CVE: CVE-2022-23638
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-14
Source: https://github.com/advisories/GHSA-fqx8-v33p-4qcc
Type: github-advisory

## Affected
- Packagist: `enshrined/svg-sanitize` — affected >=0 <0.15.0

## Details
### Impact
SVG sanitizer library before version `0.15.0` did not remove HTML elements wrapped in a CDATA section. As a result, SVG content embedded in HTML (fetched as `text/html`) was susceptible to cross-site scripting. Plain SVG files (fetched as `image/svg+xml`) were not affected.

### Patches
This issue is fixed in `0.15.0` and higher.

### Workarounds
There is currently no workaround available without upgrading.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Github](https://github.com/darylldoyle/svg-sanitizer/issues)
* Email us at [daryll@enshrined.co.uk](mailto:daryll@enshrined.co.uk)

## References
- https://github.com/darylldoyle/svg-sanitizer/security/advisories/GHSA-fqx8-v33p-4qcc
- https://nvd.nist.gov/vuln/detail/CVE-2022-23638
- https://github.com/darylldoyle/svg-sanitizer/issues/71
- https://github.com/darylldoyle/svg-sanitizer/commit/17e12ba9c2881caa6b167d0fbea555c11207fbb0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/enshrined/svg-sanitize/CVE-2022-23638.yaml
- https://github.com/advisories/GHSA-fqx8-v33p-4qcc
- https://github.com/darylldoyle/svg-sanitizer
