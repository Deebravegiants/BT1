# [M] Craft CMS 5.0.0-RC1 before 5.10.6 Path Traversal via ensurePathIsContained

## Summary
Severity: Medium
Advisory: CVE-2026-72783
Aliases: GHSA-7hxc-f267-h5q7
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72783
Type: osv

## Details
Craft CMS versions >= 5.0.0-RC1 before 5.10.6 and >= 4.0.0-RC1 before 4.18.2 contain a theoretical path traversal weakness in the ensurePathIsContained function of the Local file system class. The order of operations validates the path before normalization, so normalization could invalidate prior validation assumptions (a desanitization-style issue) and potentially resolve to files outside the intended volume directory. The vendor notes the issue is not directly exploitable and no exploitable scenario has been discovered; the fix is recommended for hardening.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72783.json
- https://github.com/craftcms/cms/security/advisories/GHSA-7hxc-f267-h5q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-72783
- https://www.vulncheck.com/advisories/craft-cms-rc1-before-path-traversal-via-ensurepathiscontained
