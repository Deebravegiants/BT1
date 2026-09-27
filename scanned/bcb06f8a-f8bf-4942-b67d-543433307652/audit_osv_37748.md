# [H] Frigate has insecure password change functionality

## Summary
Severity: High
Advisory: CVE-2026-33124
Aliases: GHSA-24p8-r573-vwr2
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33124
Type: osv

## Details
Frigate is a network video recorder (NVR) with realtime local object detection for IP cameras. Versions prior to 0.17.0-beta1 allow any authenticated user to change their own password without verifying the current password through the /users/{username}/password endpoint. Changing a password does not invalidate existing JWT tokens, and there is no validation of password strength. If an attacker obtains a valid session token (e.g., via accidentally exposed JWT, stolen cookie, XSS, compromised device, or sniffing over HTTP), they can change the victim’s password and gain permanent control of the account. Since password changes do not invalidate existing JWT tokens, session hijacks persist even after a password reset. Additionally, the lack of password strength validation exposes accounts to brute-force attacks. This issue has been resolved in version 0.17.0-beta1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33124.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-24p8-r573-vwr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33124
- https://github.com/blakeblackshear/frigate/commit/152e58520614610988bff3b6ff55d0aefd89c1b2
