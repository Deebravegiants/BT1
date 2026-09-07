# [M] Feehi CMS has an authenticated stored cross-site scripting (XSS) vulnerability via the Role Management module

## Summary
Severity: Medium
Advisory: GHSA-hqjc-wfvx-x2fv
CVE: CVE-2026-31352
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-hqjc-wfvx-x2fv
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected 2.1.1

## Details
An authenticated stored cross-site scripting (XSS) vulnerability in the Role Management module of Feehi CMS v2.1.1 allows attackers to execute arbitrary web scripts or HTML via injecting a crafted payload into the Role Name parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31352
- https://github.com/liufee/cms/issues/83
- https://github.com/liufee/cms
