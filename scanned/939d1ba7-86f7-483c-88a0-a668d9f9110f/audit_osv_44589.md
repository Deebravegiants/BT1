# [M] Craft CMS 5.0.0 through 5.10.10 Authorization Bypass via assets/move-asset

## Summary
Severity: Medium
Advisory: CVE-2026-84794
Aliases: GHSA-9xvf-7w97-83mv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84794
Type: osv

## Details
Craft CMS versions before 5.10.11 lack authorization checks in the assets/move-asset endpoint when force=1 is supplied. Authenticated users without peer asset permissions can move their own assets into other users' folders and force deletion of conflicting files, allowing unauthorized asset deletion and replacement.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84794.json
- https://github.com/craftcms/cms/security/advisories/GHSA-9xvf-7w97-83mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-84794
- https://www.vulncheck.com/advisories/craft-cms-5.0.0-through-5.10.10-authorization-bypass-via-assets-move-asset
