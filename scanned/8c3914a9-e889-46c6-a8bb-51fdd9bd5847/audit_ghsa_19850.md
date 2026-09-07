# [M] Umbraco Allows a Restricted Editor User to Delete Media Item or Access Unauthorized Content

## Summary
Severity: Medium
Advisory: GHSA-wx5h-wqfq-v698
CVE: CVE-2025-27602
CWE: CWE-285, CWE-863
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-wx5h-wqfq-v698
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Web.Backoffice` — affected >=0 <10.8.9
- NuGet: `Umbraco.Cms.Web.Backoffice` — affected >=11.0.0-rc1 <13.7.1

## Details
### Impact
Via manipulation of backoffice API URLs it's possible for authenticated backoffice users to retrieve or delete content or media held within folders the editor does not have access to.

### Patches
Will be patched in 10.8.9 and 13.7.1

### Workarounds
None available.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-wx5h-wqfq-v698
- https://nvd.nist.gov/vuln/detail/CVE-2025-27602
- https://github.com/umbraco/Umbraco-CMS/commit/5b54bed406682ceff57903bf7d3c57814eef31a7
- https://github.com/umbraco/Umbraco-CMS/commit/7888b9a4ce5ae7f9bda7ff3bb705b8fcd2f1675d
- https://github.com/umbraco/Umbraco-CMS
