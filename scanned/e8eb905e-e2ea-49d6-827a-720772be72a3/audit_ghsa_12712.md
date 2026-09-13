# [H] passport-wsfed-saml2 Signature Bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-5wrg-8fxp-cx9r
Ecosystem: npm
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-5wrg-8fxp-cx9r
Type: github-advisory

## Affected
- npm: `passport-wsfed-saml2` — affected >=0 <3.0.10

## Details
## Information
Please note that this is not a new disclosure, and is previously reported in our [SECURITY-NOTICE.md](https://github.com/auth0/passport-wsfed-saml2/commit/520b9fc0bb4249ce83bec47e30153419f086ab70
) which we removed in favor of github advisory. 

# Overview

A vulnerability was found in the validation of a SAML signature. The validation doesn't ensure that the "Signature" tag is at the proper location inside an "Assertion" tag. This leads to a signature relocation attack where the attacker can corrupt one field of data while maintaining the signature valid. This could allow an authenticated attacker to "remove" one group from the assertion or corrupt another field of an assertion.

# Am I affected?

You are affected if you are using the passport-wsfed-saml2 library to version < 3.0.10

# How do I fix it?

You may fix this issue by upgrading passport-wsfed-saml2 library to version 3.0.10 or above. 

# Will the fix impact my users?

This fix patches the library that your application runs, but will not impact your users, their current state, or any existing sessions.

## References
- https://github.com/auth0/passport-wsfed-saml2/security/advisories/GHSA-5wrg-8fxp-cx9r
- https://github.com/auth0/passport-wsfed-saml2/pull/79
- https://github.com/auth0/passport-wsfed-saml2/commit/f75211d42d2586a0d24a9da29ba8590e42363500
- https://github.com/auth0/passport-wsfed-saml2
