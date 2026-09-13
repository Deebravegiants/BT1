# [C] Grav API Plugin 1.0.9 Privilege Escalation via Invitations groups

## Summary
Severity: Critical
Advisory: CVE-2026-65897
Aliases: GHSA-m86m-jjcg-gcvv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65897
Type: osv

## Details
Grav API Plugin versions before 1.0.10 fail to validate the groups field in InvitationsController::create(), allowing authenticated api.users.write callers to assign invited accounts to groups that grant api.super permissions. Attackers can create invitation records with elevated group membership, and when accepted, the new account gains full super-admin API access without the inviter holding those permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65897.json
- https://github.com/getgrav/grav/security/advisories/GHSA-m86m-jjcg-gcvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-65897
- https://www.vulncheck.com/advisories/grav-api-plugin-privilege-escalation-via-invitations-groups
- https://github.com/getgrav/grav-plugin-api/commit/f9438d4e71389b1041ac60b69b0b5714ecfa3bdd
- https://github.com/getgrav/grav/commit/345e79e3abf8c15f80e612a09f6643300071324b
