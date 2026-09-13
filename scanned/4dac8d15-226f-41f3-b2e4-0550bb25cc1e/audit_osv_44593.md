# [C] Craft CMS 5.0.0-RC1 before 5.10.11 Authentication Bypass via administrateUsers

## Summary
Severity: Critical
Advisory: CVE-2026-84801
Aliases: GHSA-6qw4-cjqw-fj72
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84801
Type: osv

## Details
Craft CMS versions before 5.10.11 fail to validate admin status in the actionGetPasswordResetUrl endpoint, allowing non-admin users with administrateUsers permission to mint password reset URLs for administrator accounts. Attackers can generate a valid reset URL for any admin user and set a new password via actionSetPassword, which validates only the verification code without checking the caller's session, enabling complete control-panel takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84801.json
- https://github.com/craftcms/cms/security/advisories/GHSA-6qw4-cjqw-fj72
- https://nvd.nist.gov/vuln/detail/CVE-2026-84801
- https://www.vulncheck.com/advisories/craft-cms-5.0.0-rc1-before-5.10.11-authentication-bypass-via-administrateusers
