# [M] PyroCMS Vulnerable to CSRF

## Summary
Severity: Medium
Advisory: GHSA-56xx-pv88-2662
CVE: CVE-2020-25262
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-56xx-pv88-2662
Type: github-advisory

## Affected
- Packagist: `pyrocms/pyrocms` — affected >=0

## Details
PyroCMS 3.7 is vulnerable to cross-site request forgery (CSRF) via the `admin/pages/delete/` URI: pages will be deleted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25262
- https://gist.github.com/farid007/2af454d909fa5a60a07e4e547e99964e
- https://github.com/pyrocms/pyrocms
