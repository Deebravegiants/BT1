# [M] Combodo iTop: Version disclosure via login page logo

## Summary
Severity: Medium
Advisory: CVE-2026-27463
Aliases: GHSA-hm9q-8jx3-f3v5
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-27463
Type: osv

## Details
Combodo iTop is a web based IT service management tool. Prior to 3.2.3, the HTML title attribute of the logo in the login page contains the complete iTop version. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27463.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-hm9q-8jx3-f3v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27463
- https://github.com/Combodo/iTop/commit/d124f8ee58fa243193184ac2c55a561acdded356
