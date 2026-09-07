# [C] @nfid/embed has compromised private key due to @dfinity/auth-client producing insecure session keys

## Summary
Severity: Critical
Advisory: GHSA-84c3-j8r2-mcm8
CWE: CWE-321, CWE-330
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-26
Source: https://github.com/advisories/GHSA-84c3-j8r2-mcm8
Type: github-advisory

## Affected
- npm: `@nfid/embed` — affected >=0.10.0 <0.10.1-alpha.6

## Details
### Problem
User sessions in the @nfid/embed SDK with Ed25519 keys are vulnerable due to a compromised private key `535yc-uxytb-gfk7h-tny7p-vjkoe-i4krp-3qmcl-uqfgr-cpgej-yqtjq-rqe`. This exposes users to potential loss of funds on ledgers and unauthorized access to canisters they control.

### Solution
Using version >1.0.1 of @dfinity/auth-client and @dfinity/identity packages, or @nfid/embed >0.10.1-alpha.6 includes patched versions of the issue.

User sessions will be automatically fixed when they re-authenticate.

### Why this happened
The DFINITY auth client library provides a function, `Ed25519KeyIdentity.generate`, for generating an Ed25519 key pair. This function includes an optional parameter to supply a 32-byte seed value, which will be utilized as the secret key. In cases where no seed value is provided, the library is expected to generate the secret key using secure randomness. However, a recent update of DFINITY libraries has compromised this assurance by employing an insecure seed for key pair generation.

### References
[AgentJS CVE ](https://github.com/dfinity/agent-js/security/advisories/GHSA-c9vv-fhgv-cjc3)

## References
- https://github.com/dfinity/agent-js/security/advisories/GHSA-c9vv-fhgv-cjc3
- https://github.com/internet-identity-labs/sdk-ts/security/advisories/GHSA-84c3-j8r2-mcm8
- https://github.com/internet-identity-labs/sdk-ts
