# [H] Total.js CMS Unauthorized Access

## Summary
Severity: High
Advisory: GHSA-q3x9-28f7-w8rc
CVE: CVE-2019-15953
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q3x9-28f7-w8rc
Type: github-advisory

## Affected
- npm: `total4` — affected 12.0

## Details
An issue was discovered in Total.js CMS 12.0.0. An authenticated user with limited privileges can get access to a resource that they do not own by calling the associated API. The product correctly manages privileges only for the front-end resource path, not for API requests. This leads to vertical and horizontal privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15953
- https://github.com/beerpwn/CVE/blob/master/Totaljs_disclosure_report/report_final.pdf
- https://github.com/totaljs/cms
- https://seclists.org/fulldisclosure/2019/Sep/6
