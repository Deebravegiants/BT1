# [H] Samlify is vulnerable to signature wrapping

## Summary
Severity: High (CVSS 8.0)
Program: Node.js third-party modules
Weakness: Cryptographic Issues - Generic
Reporter: webtonull
State: resolved
Disclosed: 2018-10-23T07:54:50.161Z
Source: https://hackerone.com/reports/356284

## Details
I would like to report a signature wrapping weakness in samlify
It allows an attacker to modify a SAML token received from the IdP before validating it with the service provider

# Module

**module name:** samlify
**version:** 2.3.7
**npm page:** `https://www.npmjs.com/package/samlify`

## Module Description

Highly configuarable Node.js SAML 2.0 library for Single Sign On

## Module Stats

> Replace stats below with numbers from npm’s module page:

1084 downloads in the last week

# Vulnerability

## Vulnerability Description

It's possible to wrap the signature of a SAML response, and insert a new username in the original token, thus make it appear as though a different user was authenticated.

## Steps To Reproduce:

Clone the github repo, put this in `test/flow.ts` and run `npm run test`:
```

test('should reject signature wrapped response', async t => {
  // sender (caution: only use metadata and public key when declare pair-up in oppoent entity)
  const user = { email: 'user@esaml2.com' };
  const { id, context: SAMLResponse } = await idpNoEncrypt.createLoginResponse(sp, sampleRequestInfo, 'post', user, createTemplateCallback(idpNoEncrypt, sp, user));
  // receiver (caution: only use metadata and public key when declare pair-up in oppoent entity)

  //Decode
  var buffer = new Buffer(SAMLResponse, "base64");
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/356284_
