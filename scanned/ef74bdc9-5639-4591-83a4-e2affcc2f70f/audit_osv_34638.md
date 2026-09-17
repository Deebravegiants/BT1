# [M] PILOS is missing session regeneration after password change

## Summary
Severity: Medium
Advisory: CVE-2025-62781
Aliases: GHSA-m8w5-8w3h-72wm
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-62781
Type: osv

## Details
PILOS (Platform for Interactive Live-Online Seminars) is a frontend for BigBlueButton. Prior to 4.8.0, users with a local account can change their password while logged in. When doing so, all other active sessions are terminated, except for the currently active one. However, the current session’s token remains valid and is not refreshed. If an attacker has previously obtained this session token through another vulnerability, changing the password will not invalidate their access. As a result, the attacker can continue to act as the user even after the password has been changed. This vulnerability is fixed in 4.8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62781.json
- https://github.com/THM-Health/PILOS/security/advisories/GHSA-m8w5-8w3h-72wm
- https://nvd.nist.gov/vuln/detail/CVE-2025-62781
