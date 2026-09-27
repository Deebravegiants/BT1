# [M] CasaOS Username Enumeration

## Summary
Severity: Medium
Advisory: GHSA-c967-2652-gfjm
CVE: CVE-2024-24766
CWE: CWE-204
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-c967-2652-gfjm
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS-UserService` — affected >=0.4.4.3 <0.4.7

## Details
### Summary

The Casa OS Login page has disclosed the username enumeration vulnerability in the login page.

### Details

It is observed that the attacker can enumerate the CasaOS username using the application response. If the username is incorrect application gives the error "**User does not exist**",  If the password is incorrect application gives the error "**Invalid password**". 

### PoC

Capture the login request in a tool like Burp Suit and use the intruder tab for trying multiple usernames. 
Keep checking the response of each request if the response says **Invalid password** then the username is right.

### Impact

Using this error attacker can enumerate the username of CasaOS. 

### The logic behind the issue

If the username is incorrect, then throw an error "User does not exist" else throw an error "Invalid password".

This condition can be vice versa like:

If the password is incorrect, then throw an error "Invalid password" else throw an error "User does not exist".

### Mitigation

Since this is the condition we have to implement a single error which can be "Username/Password is Incorrect!!!"

## References
- https://github.com/IceWhaleTech/CasaOS-UserService/security/advisories/GHSA-c967-2652-gfjm
- https://nvd.nist.gov/vuln/detail/CVE-2024-24766
- https://github.com/IceWhaleTech/CasaOS-UserService/commit/c75063d7ca5800948e9c09c0a6efe9809b5d39f7
- https://github.com/IceWhaleTech/CasaOS-UserService
- https://github.com/IceWhaleTech/CasaOS-UserService/releases/tag/v0.4.7
