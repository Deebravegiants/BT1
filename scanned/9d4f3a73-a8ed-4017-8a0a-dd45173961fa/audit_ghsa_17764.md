# [M] TYPO3-EXT-SA-2025-001: Account Takeover in extension "OpenID Connect Authentication" (oidc)

## Summary
Severity: Medium
Advisory: GHSA-hj78-p4h7-m5fv
CVE: CVE-2025-24856
CWE: CWE-288, CWE-348, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-hj78-p4h7-m5fv
Type: github-advisory

## Affected
- Packagist: `causal/oidc` — affected >=3.0.0 <4.0.0

## Details
## Problem Description
A vulnerability in the account linking logic of the extension allows a pre-hijacking attack leading to Account Takeover. The attack can only be exploited if the following requirements are met:

- An attacker can anticipate the email address of the user.
- An attacker can register a public frontend user account using that email address before the user's first OIDC login.
- The IDP returns the field email containing the email address of the user

## Solution
An updated versions 4.0.0 is available from the TYPO3 extension manager, packagist and at 
https://extensions.typo3.org/extension/download/oidc/4.0.0/zip

Users of the extension are advised to update the extension as soon as possible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24856
- https://github.com/xperseguers/t3ext-oidc/commit/877e09f6faf4c87bbb41233112ec7e30d3c902b3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/causal/oidc/CVE-2025-24856.yaml
- https://typo3.org/security/advisory/typo3-ext-sa-2025-001
