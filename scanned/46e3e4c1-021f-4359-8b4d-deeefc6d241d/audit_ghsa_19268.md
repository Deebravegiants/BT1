# [H] Passport-wsfed-saml2 allows SAML Authentication Bypass via Attribute Smuggling

## Summary
Severity: High
Advisory: GHSA-8gqj-226h-gm8r
CVE: CVE-2025-46573
CWE: CWE-287, CWE-290
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-8gqj-226h-gm8r
Type: github-advisory

## Affected
- npm: `passport-wsfed-saml2` — affected >=3.0.5 <4.6.4

## Details
### Overview
This vulnerability allows an attacker to impersonate any user during SAML authentication by tampering with a valid SAML response. This can be done by adding attributes to the response.

### Am I Affected?
You are affected by this SAML Attribute Smuggling vulnerability if you are using `passport-wsfed-saml2` version 4.6.3 or below, specifically under the following conditions:
1. The service provider is using `passport-wsfed-saml2`, 
2. A valid SAML Response signed by the Identity Provider can be obtained

### Fix
Upgrade to v4.6.4 or greater.

## References
- https://github.com/auth0/passport-wsfed-saml2/security/advisories/GHSA-8gqj-226h-gm8r
- https://nvd.nist.gov/vuln/detail/CVE-2025-46573
- https://github.com/auth0/passport-wsfed-saml2/commit/e5cf3cc2a53748207f7a81bfba9195c8efa94181
- https://github.com/auth0/passport-wsfed-saml2
