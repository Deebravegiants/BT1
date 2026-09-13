# [M] Sensitive Information Disclosure abusing SQL Injection in Xibo CMS dataset filter

## Summary
Severity: Medium
Advisory: CVE-2023-33178
Aliases: GHSA-g9x2-757j-hmhh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33178
Type: osv

## Details
Xibo is a content management system (CMS). An SQL injection vulnerability was discovered in the `/dataset/data/{id}` API route inside the CMS starting in version 1.4.0 and prior to versions 2.3.17 and 3.3.5. This allows an authenticated user to exfiltrate data from the Xibo database by injecting specially crafted values in to the `filter` parameter. Values allowed in the filter parameter are checked against a deny list of commands that should not be allowed, however this checking was done in a case sensitive manor and so it is possible to bypass these checks by using unusual case combinations. Users should upgrade to version 2.3.17 or 3.3.5, which fix this issue. There are no workarounds aside from upgrading.

## References
- https://claroty.com/team82/disclosure-dashboard
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33178.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-g9x2-757j-hmhh
- https://nvd.nist.gov/vuln/detail/CVE-2023-33178
- https://xibosignage.com/blog/security-advisory-2023-05/
