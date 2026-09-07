# [M] Feehi CMS has an authenticated stored cross-site scripting (XSS) vulnerability via the Page Sign parameter

## Summary
Severity: Medium
Advisory: GHSA-cgxr-v74v-g9mm
CVE: CVE-2026-31350
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-cgxr-v74v-g9mm
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected 2.1.1

## Details
An authenticated stored cross-site scripting (XSS) vulnerability in Feehi CMS v2.1.1 allows attackers to execute arbitrary web scripts or HTML via injecting a crafted payload into the Page Sign parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31350
- https://github.com/liufee/cms/issues/82
- https://github.com/liufee/cms
