# [H] CubeFS timing attack can leak user passwords

## Summary
Severity: High
Advisory: GHSA-8579-7p32-f398
CVE: CVE-2023-46739
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-8579-7p32-f398
Type: github-advisory

## Affected
- Go: `github.com/cubefs/cubefs` — affected >=0 <3.3.1

## Details
A vulnerability was found during in the CubeFS master component that could allow an untrusted attacker to steal user passwords by carrying out a timing attack. The root case of the vulnerability was that CubeFS used raw string comparison of passwords.

The vulnerable part of CubeFS was the UserService of the master component. The UserService gets instantiated when starting the server of the master component. 

CubeFS has not seen any evidence of this being exploited in the wild. The vulnerability was found during a security audit conducted by [Ada Logics](https://adalogics.com/) in collaboration with [OSTIF](https://ostif.org/) and the [CNCF](https://www.cncf.io/).

The issue has been patched in v3.3.1. For impacted users, there is no other way to mitigate the issue besides upgrading.

## References
- https://github.com/cubefs/cubefs/security/advisories/GHSA-8579-7p32-f398
- https://nvd.nist.gov/vuln/detail/CVE-2023-46739
- https://github.com/cubefs/cubefs/commit/6a0d5fa45a77ff20c752fa9e44738bf5d86c84bd
- https://github.com/cubefs/cubefs/commit/c21d034d2fcd051ffd64afeafc68cbcb39d26551
- https://github.com/cubefs/cubefs
