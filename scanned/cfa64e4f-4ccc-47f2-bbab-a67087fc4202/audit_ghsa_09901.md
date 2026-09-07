# [M] Feehi CMS has authenticated stored cross-site scripting (XSS) vulnerabilities via the Permissions module

## Summary
Severity: Medium
Advisory: GHSA-xqm9-6qmm-xrqh
CVE: CVE-2026-31354
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-xqm9-6qmm-xrqh
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected 2.1.1

## Details
Multiple authenticated stored cross-site scripting (XSS) vulnerabilities in the Permissions module of Feehi CMS v2.1.1 allows attackers to execute arbitrary web scripts or HTML via injecting a crafted payload into the Group, Category or Description parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31354
- https://github.com/liufee/cms/issues/85
- https://github.com/liufee/cms
