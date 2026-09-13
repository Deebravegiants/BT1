# [H] Oqtane Framework Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-995c-qww8-64fj
CVE: CVE-2024-55470
CWE: CWE-290
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-995c-qww8-64fj
Type: github-advisory

## Affected
- NuGet: `Oqtane.Framework` — affected >=0
- NuGet: `Oqtane.Server` — affected >=0

## Details
Oqtane Framework 6.0.0 is vulnerable to Incorrect Access Control. By manipulating the entityid parameter, attackers can bypass passcode validation and successfully log into the application or access restricted data without proper authorization. The lack of server-side validation exacerbates the issue, as the application relies on client-side information for authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55470
- https://github.com/oqtane/oqtane.framework/pull/4878/files
- https://gist.github.com/Kaushikjoshi/2d8ad350ba5e72030fcee2536498cfe4
- https://github.com/oqtane/oqtane.framework
