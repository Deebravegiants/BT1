# [M] Xibo CMS has Preview and SavedReport IDOR via disableUserCheck without controller-level authorization

## Summary
Severity: Medium
Advisory: CVE-2026-31956
Aliases: GHSA-q6rv-8hhj-3fr8
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31956
Type: osv

## Details
Xibo is an open source digital signage platform with a web content management system and Windows display player software. Prior to version 4.4.1, any authenticated user can manually construct a URL to preview campaigns/regions, and export saved reports belonging to other users. Exploitation of the vulnerability is possible on behalf of an authorized user who has any of the following privileges: Page which shows all Layouts that have been created for the purposes of Layout Management; page which shows all Campaigns that have been created for the purposes of Campaign Management; and page which shows all Reports that have been Saved. Users should upgrade to version 4.4.1 which fixes this issue. Upgrading to a fixed version is necessary to remediate.

## References
- https://github.com/xibosignage/xibo-cms/releases/tag/4.4.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31956.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-q6rv-8hhj-3fr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-31956
