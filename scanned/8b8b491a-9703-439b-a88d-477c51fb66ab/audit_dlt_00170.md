# [H] Prototype Pollution

## Summary
Severity: High
Chain: Tooling
Component: web3/web3.js
CVE: CVE-2024-21505
Published: 2024-03-27
Source: https://github.com/web3/web3.js/security/advisories/GHSA-2g4c-8fpm-c46v
Type: github-advisory

## Details
### Impact: 
The mergeDeep() function in the web3-utils package has been identified for Prototype Pollution vulnerability. An attacker has the ability to modify an object's prototype, which could result in changing the behavior of all objects that inherit from the impacted prototype by providing carefully crafted input to function.

### Patches: 
It has been fixed in web3-utils version 4.2.1 so all packages and apps depending on web3-utils >=4.0.1 and <=4.2.0 should upgrade to web3-utils 4.2.1.

### Workarounds: 
None
