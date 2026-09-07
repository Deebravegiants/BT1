# [C] Winter vulnerable to privilege escalation by authenticated backend users

## Summary
Severity: Critical
Advisory: GHSA-pgpf-m8m4-6cg6
CVE: CVE-2026-27591
CWE: CWE-284, CWE-639, CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-pgpf-m8m4-6cg6
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=1.2.0 <1.2.12
- Packagist: `winter/wn-backend-module` — affected >=1.1.0 <1.1.12
- Packagist: `winter/wn-backend-module` — affected >=0 <1.0.477

## Details
## Impact
Affected versions of Winter CMS allowed authenticated backend users to escalate their accounts level of access to the system by modifying the roles / permissions assigned to their account through specially crafted requests to the backend while logged in.

To actively exploit this security issue, an attacker would need access to the Backend with a user account with any level of access.

The Winter CMS maintainers strongly recommend that all Winter CMS sites that have any reliance on the roles & permissions system to update immediately. Security fixes have been backported to all major versions of Winter (1.0, 1.1, and 1.2).

## Patches
Multiple fixes and defence in depth has been applied to prevent current and future privilege escalation attacks at the lowest level possible.

This security issue has been fixed as of https://wintercms.com/releases/v1.0.477, https://wintercms.com/releases/v1.1.12, https://wintercms.com/releases/v1.2.12.

## Workarounds
If you cannot upgrade, you may apply the changes from the releases to your Winter CMS installation manually to resolve this issue.

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-pgpf-m8m4-6cg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27591
- https://github.com/wintercms/winter
- https://wintercms.com/releases/v1.0.477
- https://wintercms.com/releases/v1.1.12
- https://wintercms.com/releases/v1.2.12
