# [H] acf-to-rest-api plugin insecure direct object reference (IDOR) via permalink manipulation

## Summary
Severity: High
Advisory: GHSA-r345-x8hr-2r9p
CVE: CVE-2020-13700
CWE: CWE-200, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r345-x8hr-2r9p
Type: github-advisory

## Affected
- Packagist: `airesvsg/acf-to-rest-api` — affected >=0

## Details
An issue was discovered in the acf-to-rest-api plugin through 3.1.0 for WordPress. It allows an insecure direct object reference via permalinks manipulation, as demonstrated by a `wp-json/acf/v3/options/` request that reads sensitive information in the `wp_options` table, such as the login and pass values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13700
- https://gist.github.com/mariuszpoplwski/4fbaab7f271bea99c733e3f2a4bafbb5
- https://github.com/airesvsg/acf-to-rest-api
- https://wordpress.org/plugins/acf-to-rest-api/#developers
