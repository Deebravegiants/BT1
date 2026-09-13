# [M] XWiki AdminTools application doesn't set permissions on the AdminTools space

## Summary
Severity: Medium
Advisory: GHSA-v7r8-8p5c-h4xw
CVE: CVE-2025-54990
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-v7r8-8p5c-h4xw
Type: github-advisory

## Affected
- Maven: `com.xwiki.admintools:application-admintools` — affected >=0 <1.1

## Details
### Impact

Users without admin rights have access to `AdminTools.SpammedPages`. 

### Details
View rights are not restricted only to admin users for `AdminTools.SpammedPages`. While no data is visible to non admin users, the page is still accessible.

### Workarounds
Set the view rights for the `AdminTools` space to be only available for the `XWikiAdminGroup`.

## References
- https://github.com/xwikisas/application-admintools/security/advisories/GHSA-v7r8-8p5c-h4xw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54990
- https://github.com/xwikisas/application-admintools
