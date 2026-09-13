# [H] Velociraptor OIDC Authenticator susceptible to email spoofing

## Summary
Severity: High
Advisory: CVE-2026-18639
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18639
Type: osv

## Details
When Velociraptor is configured to use an OIDC IdP for authentication, it uses the email claim as a username. However, some IdP allow users to change the email claim without verification. Some IdPs do not set the "email_verified" claim and do not actually verify the email.

This allows a user to impersonate another user by setting their email address within the IdP, allowing account takeover.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18639/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18639.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18639
