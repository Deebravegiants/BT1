# [M] Cross-site scripting in forkcms

## Summary
Severity: Medium
Advisory: GHSA-3374-7h99-xr85
CVE: CVE-2020-23049
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-25
Source: https://github.com/advisories/GHSA-3374-7h99-xr85
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.8.1

## Details
Fork CMS Content Management System v5.8.0 was discovered to contain a cross-site scripting (XSS) vulnerability in the `Displayname` field when using the `Add`, `Edit` or `Register' functions. This vulnerability allows attackers to execute arbitrary web scripts or HTML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23049
- https://github.com/forkcms/forkcms/commit/6ec6171206a7507a39695edc8bbd1b97ef1041c6
- https://github.com/forkcms/forkcms
- https://www.vulnerability-lab.com/get_content.php?id=2208
