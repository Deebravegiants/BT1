# [H] CVE-2021-27935

## Summary
Severity: High
Advisory: CVE-2021-27935
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2021-27935
Type: osv

## Details
An issue was discovered in AdGuard before 0.105.2. An attacker able to get the user's cookie is able to bruteforce their password offline, because the hash of the password is stored in the cookie.

## References
- https://github.com/AdguardTeam/AdGuardHome/issues/2470
