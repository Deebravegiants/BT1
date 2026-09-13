# [H] passport-wsfed-saml2 vulnerable to Signature Bypass in SAML2 token

## Summary
Severity: High
Advisory: GHSA-77fw-rf4v-vfp9
CVE: CVE-2017-16897
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-77fw-rf4v-vfp9
Type: github-advisory

## Affected
- npm: `passport-wsfed-saml2` — affected >=0 <3.0.5

## Details
## Information
Please note that this is not a new disclosure, and is previously reported in our [SECURITY-NOTICE.md](https://github.com/auth0/passport-wsfed-saml2/commit/520b9fc0bb4249ce83bec47e30153419f086ab70
) which we removed in favor of github advisory. 

# Overview 
 This vulnerability allows an attacker to impersonate another user and potentially elevate their privileges if the SAML identity provider:

- signs SAML response and signs assertion

- does not sign SAML response and signs assertion

# Am I affected?

You may be affected if you use SAML2 protocol with passport-wsfed-saml2 versions below 3.0.5 and your SAML identity Provider: 
1. signs SAML response and signs assertion; or 
2. does not sign SAML response and signs assertion

# How do I fix it?

You may fix this vulnerability by upgrading your library to version 3.0.5 or above. 

# Will the fix impact my users?
This fix patches the library that your application runs, but will not impact your users, their current state, or any existing sessions.

## References
- https://github.com/auth0/passport-wsfed-saml2/security/advisories/GHSA-77fw-rf4v-vfp9
- https://nvd.nist.gov/vuln/detail/CVE-2017-16897
- https://github.com/auth0/passport-wsfed-saml2/commit/520b9fc0bb4249ce83bec47e30153419f086ab70
- https://auth0.com/docs/security/bulletins/cve-2017-16897
- https://github.com/auth0/passport-wsfed-saml2
