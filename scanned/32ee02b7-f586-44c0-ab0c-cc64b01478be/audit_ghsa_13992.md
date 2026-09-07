# [M] Dcat-Admin vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-p74v-mwvg-8ghp
CVE: CVE-2023-33736
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-31
Source: https://github.com/advisories/GHSA-p74v-mwvg-8ghp
Type: github-advisory

## Affected
- Packagist: `dcat/laravel-admin` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability in Dcat-Admin v2.1.3-beta allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the URL parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33736
- https://github.com/jqhph/dcat-admin/issues/2027
- https://github.com/jqhph/dcat-admin
