# [H] Secret encryption vulnerable to brute-force attacks

## Summary
Severity: High
Advisory: CVE-2024-45394
Aliases: GHSA-gv8m-vgp8-q2xr
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-45394
Type: osv

## Details
Authenticator is a browser extension that generates two-step verification codes. In versions 7.0.0 and below, encryption keys for user data were stored encrypted at-rest using only AES-256 and the EVP_BytesToKey KDF. Therefore, attackers with a copy of a user's data are able to brute-force the user's encryption key. Users on version 8.0.0 and above are automatically migrated away from the weak encoding on first login. Users should destroy encrypted backups made with versions prior to 8.0.0.

## References
- https://github.com/Authenticator-Extension/Authenticator/security/advisories/GHSA-gv8m-vgp8-q2xr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45394.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45394
- https://github.com/Authenticator-Extension/Authenticator/commit/17aa2068553db3c3aac081c9ffe393536f33b28b
