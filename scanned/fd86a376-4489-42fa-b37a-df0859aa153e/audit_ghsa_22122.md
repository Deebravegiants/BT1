# [M] Improper Neutralization of Input During Web Page Generation in Select2

## Summary
Severity: Medium
Advisory: GHSA-rf66-hmqf-q3fc
CVE: CVE-2016-10744
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rf66-hmqf-q3fc
Type: github-advisory

## Affected
- npm: `select2` — affected >=0 <4.0.6

## Details
In Select2 through 4.0.5, as used in Snipe-IT and other products, rich selectlists allow XSS. This affects use cases with Ajax remote data loading when HTML templates are used to display listbox data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10744
- https://github.com/select2/select2/issues/4587
- https://github.com/snipe/snipe-it/pull/6831
- https://github.com/snipe/snipe-it/pull/6831/commits/5848d9a10c7d62c73ff6a3858edfae96a429402a
- https://github.com/select2/select2
