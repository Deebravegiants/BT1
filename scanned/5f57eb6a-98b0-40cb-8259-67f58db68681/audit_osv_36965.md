# [H] Combodo iTop: Weak secret generation for inline image

## Summary
Severity: High
Advisory: CVE-2026-27490
Aliases: GHSA-3jr5-rqmx-97gc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-27490
Type: osv

## Details
Combodo iTop is a web based IT service management tool. Prior to 3.2.3, inline images that are accessible without being authenticated are protected by a weak 24-bit pseudo-random secret. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27490.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-3jr5-rqmx-97gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27490
- http://github.com/Combodo/iTop/commit/9c39efd9af53a1deeb578133eff7333a7b8816b0
