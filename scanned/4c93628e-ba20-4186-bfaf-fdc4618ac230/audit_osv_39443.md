# [H] Termix's TOTP two-factor authentication can be disabled or bypassed using only the account password

## Summary
Severity: High
Advisory: CVE-2026-45749
Aliases: GHSA-wqfw-rqj7-fv9m
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45749
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. The `POST /users/totp/disable` and `POST /users/totp/backup-codes` endpoints in Termix prior to version 2.3.2 accept the account password as a sole authentication factor for MFA-critical operations. An attacker who obtains a user's password (phishing, credential stuffing, the passwordHash leak in GHSA-xxxx) can disable TOTP entirely or regenerate backup codes, without ever possessing the TOTP device or knowing a valid TOTP code. This renders two-factor authentication ineffective. Version 2.3.2 patches the issue.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45749.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-wqfw-rqj7-fv9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45749
