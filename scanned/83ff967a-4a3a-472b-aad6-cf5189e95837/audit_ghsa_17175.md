# [H] CasaOS-UserService allows unauthorized access to any file 

## Summary
Severity: High
Advisory: GHSA-h5gf-cmm8-cg7c
CVE: CVE-2024-24765
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-h5gf-cmm8-cg7c
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS-UserService` — affected >=0 <0.4.7

## Details
### Summary

http://demo.casaos.io/v1/users/image?path=/var/lib/casaos/1/avatar.png

Originally it was to get the url of the user's avatar, but the path filtering was not strict, making it possible to get any file on the system.


### Details

Construct paths to get any file.

Such as the CasaOS user database, and furthermore can obtain system root privileges.

### PoC

http://demo.casaos.io/v1/users/image?path=/var/lib/casaos/conf/../db/user.db

### Impact

v0.4.6 all previous versions

## References
- https://github.com/IceWhaleTech/CasaOS-UserService/security/advisories/GHSA-h5gf-cmm8-cg7c
- https://nvd.nist.gov/vuln/detail/CVE-2024-24765
- https://github.com/IceWhaleTech/CasaOS-UserService/commit/3f4558e23c0a9958f9a0e20aabc64aa8fd51840e
- https://github.com/IceWhaleTech/CasaOS-UserService
- https://github.com/IceWhaleTech/CasaOS-UserService/releases/tag/v0.4.7
