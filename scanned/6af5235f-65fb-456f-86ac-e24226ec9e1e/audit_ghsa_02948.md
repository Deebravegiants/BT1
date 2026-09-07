# [H] Improper Privilege Management in Concrete CMS 

## Summary
Severity: High
Advisory: GHSA-j4mv-2rv7-v2j9
CVE: CVE-2021-22966
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-j4mv-2rv7-v2j9
Type: github-advisory

## Affected
- Packagist: `concrete5/core` — affected >=0 <8.5.7

## Details
Privilege escalation from Editor to Admin using Groups in Concrete CMS versions 8.5.6 and below. If a group is granted "view" permissions on the bulkupdate page, then users in that group can escalate to being an administrator with a specially crafted curl. Fixed by adding a check for group permissions before allowing a group to be moved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22966
- https://hackerone.com/reports/1362747
- https://documentation.concretecms.org/developers/introduction/version-history/857-release-notes
