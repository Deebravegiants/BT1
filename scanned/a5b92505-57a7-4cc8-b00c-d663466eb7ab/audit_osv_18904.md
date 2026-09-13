# [C] CVE-2020-37172

## Summary
Severity: Critical
Advisory: CVE-2020-37172
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2020-37172
Type: osv

## Details
AVideo Platform 8.1 contains a cross-site request forgery vulnerability that allows attackers to reset user passwords by exploiting the password recovery mechanism. Attackers can craft malicious requests to the recoverPass endpoint using the user's recovery token to change account credentials without authentication.

## References
- https://avideo.com
- https://www.vulncheck.com/advisories/avideo-platform-cross-site-request-forgery-password-reset
- https://github.com/WWBN/AVideo
- https://www.exploit-db.com/exploits/48003
