# [H] SimbCo httpster vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-p8j8-wxvp-h695
CVE: CVE-2020-36629
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-p8j8-wxvp-h695
Type: github-advisory

## Affected
- npm: `httpster` — affected >=0 <1.1.0

## Details
A vulnerability classified as critical was found in SimbCo httpster. This vulnerability affects the function fs.realpathSync of the file src/server.coffee. The manipulation leads to path traversal. The exploit has been disclosed to the public and may be used. The name of the patch is d3055b3e30b40b65d30c5a06d6e053dffa7f35d0. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-216748.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36629
- https://github.com/SimbCo/httpster/pull/36
- https://github.com/SimbCo/httpster/commit/d3055b3e30b40b65d30c5a06d6e053dffa7f35d0
- https://github.com/SimbCo/httpster
- https://vuldb.com/?id.216748
