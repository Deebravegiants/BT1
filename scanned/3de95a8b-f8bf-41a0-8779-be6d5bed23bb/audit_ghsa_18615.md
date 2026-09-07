# [M] CKAN vulnerable to stored XSS in resource description

## Summary
Severity: Medium
Advisory: GHSA-2r4h-8jxv-w2j8
CVE: CVE-2025-54384
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-2r4h-8jxv-w2j8
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.11.0 <2.11.4
- PyPI: `ckan` — affected >=0 <2.10.9

## Details
### Impact

The `helpers.markdown_extract()` function did not perform sufficient sanitization of input data before wrapping in an HTML literal element. This helper is used to render user-provided data on dataset, resource, organization or group pages (plus any page provided by an extension that used that helper function), leading to a potential XSS vector.

### Patches
This vulnerability has been fixed in CKAN 2.10.9 and 2.11.4

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-2r4h-8jxv-w2j8
- https://nvd.nist.gov/vuln/detail/CVE-2025-54384
- https://github.com/ckan/ckan/commit/112affffa74b14fc97c54abcf18315df97114917
- https://github.com/ckan/ckan/commit/6d0065f2fc7e2682196d125275af34b93e9e554e
- https://github.com/ckan/ckan
- https://github.com/ckan/ckan/releases/tag/ckan-2.10.9
- https://github.com/ckan/ckan/releases/tag/ckan-2.11.4
