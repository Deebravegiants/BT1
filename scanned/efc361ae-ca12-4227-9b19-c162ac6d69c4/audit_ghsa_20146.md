# [M] Out-of-bounds Read in fast-string-search

## Summary
Severity: Medium
Advisory: GHSA-hmqg-p8f8-3qrw
CVE: CVE-2022-25872
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-18
Source: https://github.com/advisories/GHSA-hmqg-p8f8-3qrw
Type: github-advisory

## Affected
- npm: `fast-string-search` — affected >=0

## Details
All versions of package fast-string-search are vulnerable to Out-of-bounds Read due to incorrect memory freeing and length calculation for any non-string input as the source. This allows the attacker to read previously allocated memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25872
- https://github.com/magiclen/node-fast-string-search
- https://github.com/magiclen/node-fast-string-search/blob/c8dd9fc966abc80b327f509e63360f59e0de9fb5/src/fast-string-search.c%23L192
- https://snyk.io/vuln/SNYK-JS-FASTSTRINGSEARCH-2392368
