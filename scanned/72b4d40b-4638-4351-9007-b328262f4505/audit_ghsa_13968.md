# [M] Formwork Cross-site Scripting (XSS) from Page title field

## Summary
Severity: Medium
Advisory: GHSA-fvrh-wrpf-6q7h
CVE: CVE-2023-24230
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-fvrh-wrpf-6q7h
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=0 <1.13.0

## Details
### Description
A stored cross-site scripting (XSS) vulnerability in Formwork v1.12.1 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Page title field.

Only users with access to Administration Panel with page editing permission can inject raw HTML in the Page title field.

### Patched versions
This vulnerability has been patched in [Formwork 1.13.0](https://github.com/getformwork/formwork/releases/tag/1.13.0).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24230
- https://github.com/getformwork/formwork/commit/8781ee17ca9b9b7b0b57e090e7f2ba1b27dc1415
- https://github.com/getformwork/formwork
- https://medium.com/@0x2bit/formwork-1-12-1-stored-xss-vulnerability-at-page-title-b6efba27891a
