# [C] WWBN AVideo Password Recovery Token Expiration Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-84480
Aliases: GHSA-j9p7-hm85-9v77
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84480
Type: osv

## Details
WWBN AVideo fails to validate password recovery token expiration in userRecoverPassSave.json.php, allowing attackers to use expired tokens to reset account passwords indefinitely. Attackers who obtain a recovery token can use it at any time to change the target account's password and gain full account access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84480.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-j9p7-hm85-9v77
- https://nvd.nist.gov/vuln/detail/CVE-2026-84480
- https://www.vulncheck.com/advisories/wwbn-avideo-password-recovery-token-expiration-bypass
