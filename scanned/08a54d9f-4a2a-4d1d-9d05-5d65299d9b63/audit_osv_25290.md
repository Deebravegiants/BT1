# [M] Sensitive Information Disclosure abusing Stack Trace in Xibo CMS

## Summary
Severity: Medium
Advisory: CVE-2023-33181
Aliases: GHSA-c9cx-ghwr-x58m
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33181
Type: osv

## Details
Xibo is a content management system (CMS). Starting in version 3.0.0 and prior to version 3.3.5, some API routes will print a stack trace when called with missing or invalid parameters revealing sensitive information about the locations of paths that the server is using. Users should upgrade to version 3.3.5, which fixes this issue. There are no known workarounds aside from upgrading.

## References
- https://claroty.com/team82/disclosure-dashboard
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33181.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-c9cx-ghwr-x58m
- https://nvd.nist.gov/vuln/detail/CVE-2023-33181
- https://xibosignage.com/blog/security-advisory-2023-05/
