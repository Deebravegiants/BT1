# [M] Concrete CMS is vulnerable to IDOR combined with a missing authentication gate

## Summary
Severity: Medium
Advisory: GHSA-58c8-vvqw-cm7m
CVE: CVE-2026-8236
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-58c8-vvqw-cm7m
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to IDOR combined with a missing authentication gate. The endpoint /ccm/system/dialogs/file/usage/{fID} accepts an integer file ID in the URL and returns internal site structure data (page IDs, versions, URL paths) to anyone who sends a GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8236
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
