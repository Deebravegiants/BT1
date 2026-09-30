# [H] Mass Assignment Privilege Escalation in Checkmate

## Summary
Severity: High
Advisory: CVE-2026-31836
Aliases: GHSA-6368-x7wr-wpm2
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-31836
Type: osv

## Details
Checkmate is an open-source, self-hosted tool designed to track and monitor server hardware, uptime, response times, and incidents in real-time with beautiful visualizations. In versions from 3.5.1 and prior, a mass assignment vulnerability in Checkmate's user profile update endpoint allows any authenticated user to escalate their privileges to superadmin, bypassing all role-based access controls. An attacker can modify their user role to gain complete administrative access to the application, including the ability to view all users, modify critical configurations, and access sensitive system data. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31836.json
- https://github.com/bluewave-labs/Checkmate/security/advisories/GHSA-6368-x7wr-wpm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-31836
