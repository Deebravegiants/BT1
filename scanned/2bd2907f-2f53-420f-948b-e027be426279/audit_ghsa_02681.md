# [M] Cross-site scripting in ICEcoder

## Summary
Severity: Medium
Advisory: GHSA-jf9v-q8vh-3fmc
CVE: CVE-2021-32106
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-09
Source: https://github.com/advisories/GHSA-jf9v-q8vh-3fmc
Type: github-advisory

## Affected
- Packagist: `icecoder/icecoder` — affected >=0 <8.1

## Details
In ICEcoder 8.0 allows, a reflected XSS vulnerability was identified in the multipe-results.php page due to insufficient sanitization of the _GET['replace'] variable. As a result, arbitrary Javascript code can get executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32106
- https://github.com/icecoder/ICEcoder/commit/21d6ae0f2a3fce7d076ae430d48f5df56bd0f256
- https://github.com/icecoder/ICEcoder
- https://groups.google.com/g/icecoder/c/xcAc8_1UPxQ
- https://prophaze.com/cve/icecoder-8-0-multipe-results-php-replace-cross-site-scripting
