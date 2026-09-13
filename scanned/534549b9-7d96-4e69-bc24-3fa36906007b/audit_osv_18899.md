# [H] CVE-2020-37094

## Summary
Severity: High
Advisory: CVE-2020-37094
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2020-37094
Type: osv

## Details
EspoCRM 5.7.0 prior to 5.9.0 contains an authentication token reuse vulnerability that allows authenticated attackers to bypass two-factor authentication by exploiting token-to-password-hash mapping in application/Espo/Core/Utils/Authentication/Espo.php. Attackers can obtain an authentication token for a controlled account and replay it against any victim account sharing the same password, since tokens are bound to password hashes rather than unique per-user values, bypassing the victim's 2FA protections.

## References
- https://www.espocrm.com
- https://www.vulncheck.com/advisories/espocrm-two-factor-auth-bypass-via-auth-token-reuse-between-accounts-with-identical-passwords
- https://github.com/espocrm/espocrm/commit/b299220dd0c7acdaa1ed8be8ffd79c7985093c7a
- https://www.exploit-db.com/exploits/48376
