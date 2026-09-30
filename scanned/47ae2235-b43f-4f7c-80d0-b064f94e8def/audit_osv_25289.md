# [M] Sensitive Information Disclosure abusing SQL Injection in Xibo CMS display map

## Summary
Severity: Medium
Advisory: CVE-2023-33180
Aliases: GHSA-7ww5-x9rm-qm89
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33180
Type: osv

## Details
Xibo is a content management system (CMS). An SQL injection vulnerability was discovered starting in version 3.2.0 and prior to version 3.3.2 in the `/display/map` API route inside the CMS. This allows an authenticated user to exfiltrate data from the Xibo database by injecting specially crafted values in to the `bounds` parameter. Users should upgrade to version 3.3.5, which fixes this issue. There are no known workarounds aside from upgrading.

## References
- https://claroty.com/team82/disclosure-dashboard
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33180.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-7ww5-x9rm-qm89
- https://nvd.nist.gov/vuln/detail/CVE-2023-33180
- https://xibosignage.com/blog/security-advisory-2023-05/
