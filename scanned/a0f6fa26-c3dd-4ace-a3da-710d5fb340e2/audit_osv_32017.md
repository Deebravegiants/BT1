# [M] Account Takeover in NamelessMC

## Summary
Severity: Medium
Advisory: CVE-2025-22144
Aliases: GHSA-p883-7496-x35p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2025-01-13
Source: https://osv.dev/vulnerability/CVE-2025-22144
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. A user with admincp.core.emails or admincp.users.edit permissions can validate users and an attacker can reset their password. When the account is successfully approved by email the reset code is NULL, but when the account is manually validated by a user with admincp.core.emails or admincp.users.edit permissions then the reset_code will no longer be NULL but empty. An attacker can request http://localhost/nameless/index.php?route=/forgot_password/&c= and reset the password. As a result an attacker may compromise another users password and take over their account. This issue has been addressed in release version 2.1.3 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22144.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-p883-7496-x35p
- https://nvd.nist.gov/vuln/detail/CVE-2025-22144
