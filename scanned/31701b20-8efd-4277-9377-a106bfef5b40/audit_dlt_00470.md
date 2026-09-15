# [M] Fabric CA Developer's Guide: LDAP Injection via Unescaped Username in GetUser Filter

## Summary
Severity: Medium
Chain: github.com/hyperledger/fabric-ca
Component: github.com/hyperledger/fabric-ca
CVE: CVE-2026-53658
CWE: Improper Neutralization of Special Elements used in an LDAP Query ('LDAP Injection')
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-xghw-p77p-3r7x
Type: github-advisory

## Details
When fabric-ca is configured with an LDAP backend, the username from HTTP Basic authentication is included in an LDAP uid search filter without proper escaping. An unauthenticated attacker with network access to the CA enrollment endpoint could exploit this to perform LDAP injection before password validation, and potentially steer authentication attempts toward a victim account.

### Recommendation

- All users of fabric-ca with an LDAP backend should update to a fixed version.
- For users not using an LDAP backend, no action is required.
