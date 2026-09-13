# [M] People: Privilege Escalation via Missing Role Ceiling in Mail Domain Invitation

## Summary
Severity: Medium
Advisory: CVE-2026-42185
Aliases: GHSA-42cf-rv2h-v8rf
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42185
Type: osv

## Details
People is an application to handle users and teams, and distribute permissions across La Suite. Prior to version 1.25.0, a user holding the Administrator role on a mail domain could send a crafted invitation request to promote any existing user (including users with no current domain access) to the Owner role. The exploit requires a single authenticated HTTP request and grants full domain ownership immediately, without any acceptance step from the target. This issue has been patched in version 1.25.0.

## References
- https://github.com/suitenumerique/people/releases/tag/v1.25.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42185.json
- https://github.com/suitenumerique/people/security/advisories/GHSA-42cf-rv2h-v8rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-42185
- https://github.com/suitenumerique/people/commit/6a51b96d8e907483fa8fc489d8714cc35fb4099b
