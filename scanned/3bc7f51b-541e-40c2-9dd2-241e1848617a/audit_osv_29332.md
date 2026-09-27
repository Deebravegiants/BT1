# [M] Sensitive Information Disclosure abusing SQL Injection in Xibo CMS proof of play report

## Summary
Severity: Medium
Advisory: CVE-2024-41944
Aliases: GHSA-v6q4-h869-gm3r
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-41944
Type: osv

## Details
Xibo is a content management system (CMS). An SQL injection vulnerability was discovered in the `report/data/proofofplayReport` API route inside the CMS. This allows an authenticated user to to obtain and modify arbitrary data from the Xibo database by injecting specially crafted values in to the `sortBy` parameter. Users should upgrade to version 3.3.12 or 4.0.14 which fix this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41944.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-v6q4-h869-gm3r
- https://nvd.nist.gov/vuln/detail/CVE-2024-41944
- https://xibosignage.com/blog/security-advisory-2024-07
- https://github.com/xibosignage/xibo-cms/commit/c60cfd8727da77b9db10297148eadd697ebec353.patch
