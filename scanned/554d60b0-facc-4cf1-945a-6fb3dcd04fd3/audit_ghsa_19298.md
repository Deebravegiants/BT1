# [C] Passport-wsfed-saml2 allows SAML Authentication Bypass via Signature Wrapping

## Summary
Severity: Critical
Advisory: GHSA-wjmp-wphq-jvqf
CVE: CVE-2025-46572
CWE: CWE-287, CWE-347
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-wjmp-wphq-jvqf
Type: github-advisory

## Affected
- npm: `passport-wsfed-saml2` — affected >=3.0.5 <4.6.4

## Details
### Overview
This vulnerability allows an attacker to impersonate any user during SAML authentication by crafting a SAMLResponse. This can be done by using a valid SAML object that was signed by the configured IdP.

### Am I Affected?
You are affected by this SAML Signature Wrapping vulnerability if you are using `passport-wsfed-saml2` version 4.6.3 or below, specifically under the following conditions:
1. The service provider is using `passport-wsfed-saml2`,
2. A valid SAML document signed by the Identity Provider can be obtained.

### Fix
Upgrade to v4.6.4 or greater.

## References
- https://github.com/auth0/passport-wsfed-saml2/security/advisories/GHSA-wjmp-wphq-jvqf
- https://nvd.nist.gov/vuln/detail/CVE-2025-46572
- https://github.com/auth0/passport-wsfed-saml2/commit/e5cf3cc2a53748207f7a81bfba9195c8efa94181
- https://github.com/auth0/passport-wsfed-saml2
