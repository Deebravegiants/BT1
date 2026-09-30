# [H] Concrete CMS is vulnerable to missing authorization in the bulk_user_assignment.php

## Summary
Severity: High
Advisory: GHSA-g7xp-jf3x-wcx4
CVE: CVE-2026-8350
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-g7xp-jf3x-wcx4
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to missing authorization in the bulk_user_assignment.php which can lead to privilege escalation to Administrative Group. Any authenticated user with access to the bulk user assignment dashboard page can add any user email to any group and can remove legitimate admins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8350
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
