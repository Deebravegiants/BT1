# [H] Jwttoken in Cosmos server never expires after password changed and logging out

## Summary
Severity: High
Advisory: CVE-2023-49091
Aliases: GHSA-hpvm-x7m8-3c6x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-29
Source: https://osv.dev/vulnerability/CVE-2023-49091
Type: osv

## Details
Cosmos provides users the ability self-host a home server by acting as a secure gateway to your application, as well as a server manager. Cosmos-server is vulnerable due to to the authorization header used for user login remaining valid and not expiring after log out. This vulnerability allows an attacker to use the token to gain unauthorized access to the application/system even after the user has logged out. This issue has been patched in version 0.13.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49091.json
- https://github.com/azukaar/Cosmos-Server/security/advisories/GHSA-hpvm-x7m8-3c6x
- https://nvd.nist.gov/vuln/detail/CVE-2023-49091
- https://github.com/azukaar/Cosmos-Server/commit/7a3fdfb467bd4d1f8333e3e1f3c3f5fca0b69cd7
