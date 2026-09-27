# [M] CVE-2020-36968

## Summary
Severity: Medium
Advisory: CVE-2020-36968
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2020-36968
Type: osv

## Details
M/Monit 3.7.4 contains an authentication vulnerability that allows authenticated attackers to retrieve user password hashes through an administrative API endpoint. Attackers can send requests to the /api/1/admin/users/list and /api/1/admin/users/get endpoints to extract MD5 password hashes for all users.

## References
- https://mmonit.com/
- https://www.vulncheck.com/advisories/mmonit-password-disclosure
- https://www.exploit-db.com/exploits/49081
