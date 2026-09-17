# [M] CasaOS Username Enumeration - Bypass of CVE-2024-24766

## Summary
Severity: Medium
Advisory: GHSA-hcw2-2r9c-gc6p
CVE: CVE-2024-28232
CWE: CWE-204
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-01
Source: https://github.com/advisories/GHSA-hcw2-2r9c-gc6p
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS-UserService` — affected >=0.4.7 <0.4.8

## Details
### Summary

The Casa OS Login page has disclosed the username enumeration vulnerability in the login page which was patched in `CasaOS  v0.4.7`.

### Details

It is observed that the attacker can enumerate the CasaOS username using the application response. If the username is incorrect the application gives the error "**User does not exist**" with success code "**10006**", If the password is incorrect the application gives the error "**User does not exist or password is invalid**" with success code "**10013**".

### PoC

1. If the Username is invalid application gives "User does not exist" with success code "**10006**".

![1](https://github.com/IceWhaleTech/CasaOS-UserService/assets/63414468/a6eb4321-b2f3-4fba-aa8e-e1d0fbf58187)

2. If the Password is invalid application gives  "**User does not exist or password is invalid**" with success code "**10013**".

![2](https://github.com/IceWhaleTech/CasaOS-UserService/assets/63414468/126eff54-eeb0-4ee6-bc46-695376b5e5cd)


### Impact

Using this error attacker can enumerate the username of CasaOS.

### The logic behind the issue

The logic behind the issue
If the username is incorrect, then throw an error  "**User does not exist**" with success code "**10006**", else throw an error "**User does not exist or password is invalid**" with success code "**10013**".

This condition can be vice versa like:

If the password is incorrect, then throw an error "**User does not exist or password is invalid**" with success code "**10013**", else throw an error  "**User does not exist**" with success code "**10006**".

### Mitigation
Since this is the condition we have to implement a single error which can be "**Username/Password is Incorrect!!!**" with single success code.

## References
- https://github.com/IceWhaleTech/CasaOS-UserService/security/advisories/GHSA-hcw2-2r9c-gc6p
- https://nvd.nist.gov/vuln/detail/CVE-2024-28232
- https://github.com/IceWhaleTech/CasaOS-UserService/commit/dd927fe1c805e53790f73cfe10c7a4ded3bc5bdb
- https://github.com/IceWhaleTech/CasaOS-UserService
