# [H] php-svg-lib unsafe attributes merge when parsing `use` tag

## Summary
Severity: High
Advisory: CVE-2023-50252
Aliases: GHSA-jq98-9543-m4cr
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/CVE-2023-50252
Type: osv

## Details
php-svg-lib is an SVG file parsing / rendering library. Prior to version 0.5.1, when handling `<use>` tag that references an `<image>` tag, it merges the attributes from the `<use>` tag to the `<image>` tag. The problem pops up especially when the `href` attribute from the `<use>` tag has not been sanitized. This can lead to an unsafe file read that can cause PHAR Deserialization vulnerability in PHP prior to version 8. Version 0.5.1 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50252.json
- https://github.com/dompdf/php-svg-lib/security/advisories/GHSA-jq98-9543-m4cr
- https://nvd.nist.gov/vuln/detail/CVE-2023-50252
- https://github.com/dompdf/php-svg-lib/commit/08ce6a96d63ad7216315fae34a61c886dd2dc030
