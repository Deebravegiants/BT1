# [M] StudioCMS has an Authorization Bypass Through User-Controlled Key

## Summary
Severity: Medium
Advisory: CVE-2026-24134
Aliases: GHSA-8cw6-53m5-4932
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24134
Type: osv

## Details
StudioCMS is a server-side-rendered, Astro native, headless content management system. Versions prior to 0.2.0 contain a Broken Object Level Authorization (BOLA) vulnerability in the Content Management feature that allows users with the "Visitor" role to access draft content created by Editor/Admin/Owner users. Version 0.2.0 patches the issue.

## References
- https://github.com/withstudiocms/studiocms/releases/tag/studiocms%400.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24134.json
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-8cw6-53m5-4932
- https://nvd.nist.gov/vuln/detail/CVE-2026-24134
- https://github.com/withstudiocms/studiocms/commit/efc10bee20db090fdd75463622c30dda390c50ad
