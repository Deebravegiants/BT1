# [M] Artesãos SEOTools Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wjg8-pxqj-c3c7
CVE: CVE-2020-36663
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-wjg8-pxqj-c3c7
Type: github-advisory

## Affected
- Packagist: `artesaos/seotools` — affected >=0 <0.17.2

## Details
A vulnerability, which was classified as problematic, was found in Artesãos SEOTools up to and including version 0.17.1. This affects the function makeTag of the file OpenGraph.php. The manipulation of the argument value leads to open redirect. Upgrading to version 0.17.2 is able to address this issue. The name of the patch is ca27cd0edf917e0bc805227013859b8b5a1f01fb. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-222231.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36663
- https://github.com/artesaos/seotools/pull/201
- https://github.com/artesaos/seotools/commit/ca27cd0edf917e0bc805227013859b8b5a1f01fb
- https://github.com/artesaos/seotools
- https://github.com/artesaos/seotools/releases/tag/v0.17.2
- https://vuldb.com/?ctiid.222231
- https://vuldb.com/?id.222231
