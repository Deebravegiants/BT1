# [M] Stored Cross-Site Scripting (XSS) in Keycloak via groups dropdown

## Summary
Severity: Medium
Advisory: GHSA-755v-r4x4-qf7m
CWE: CWE-80
Ecosystem: Maven
Published: 2022-11-29
Source: https://github.com/advisories/GHSA-755v-r4x4-qf7m
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <20.0.0

## Details
### Summary

A Stored XSS vulnerability was reported in the Keycloak Security mailing list, affecting all the versions of Keycloak, including the latest release (16.0.1). The vulnerability allows a privileged attacker to execute malicious scripts in the admin console, abusing of the groups' dropdown functionality. 

### Impact

Successful attacks of this vulnerability can result a privileged attacker to load a XSS script, and steal data from other users. The impact can be considered moderate to low, considering privileged credentials are required.

### References
- Please refer to the Keycloak Security mailing list for more information.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-755v-r4x4-qf7m
- https://github.com/keycloak/keycloak
