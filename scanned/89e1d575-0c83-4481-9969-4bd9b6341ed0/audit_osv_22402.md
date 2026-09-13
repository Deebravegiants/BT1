# [M] CVE-2022-28977

## Summary
Severity: Medium
Advisory: CVE-2022-28977
Aliases: GHSA-w397-9p2j-6x23
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-09-22
Source: https://osv.dev/vulnerability/CVE-2022-28977
Type: osv

## Details
HtmlUtil.escapeRedirect in Liferay Portal 7.3.1 through 7.4.2, and Liferay DXP 7.0 fix pack 91 through 101, 7.1 fix pack 17 through 25, 7.2 fix pack 5 through 14, and 7.3 before service pack 3 can be circumvented by using multiple forward slashes, which allows remote attackers to redirect users to arbitrary external URLs via the (1) 'redirect` parameter (2) `FORWARD_URL` parameter, and (3) others parameters that rely on HtmlUtil.escapeRedirect.

## References
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-28977-htmlutil.escaperedirect-circumvention-with-multiple-forward-slash
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/28xxx/CVE-2022-28977.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-28977
