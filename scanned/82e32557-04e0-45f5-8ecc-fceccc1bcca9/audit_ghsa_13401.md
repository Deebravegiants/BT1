# [M] Stored Cross-Site Scripting October CMS

## Summary
Severity: Medium
Advisory: GHSA-r47v-rxcg-p28j
CVE: CVE-2023-37692
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-r47v-rxcg-p28j
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0

## Details
An svg file upload vulnerability in October CMS v3.4.4 allows attackers to execute arbitrary code in the context of a browser via a crafted svg file. Attackers must be authenticated as users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37692
- https://github.com/octobercms/october
- https://okankurtulus.com.tr/2023/07/24/october-cms-v3-4-4-stored-cross-site-scripting-xss-authenticated
