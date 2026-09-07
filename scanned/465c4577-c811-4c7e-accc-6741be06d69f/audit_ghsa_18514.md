# [M] DiracX-Web is vulnerable to attack through an Open Redirect on its login page

## Summary
Severity: Medium
Advisory: GHSA-hfj7-542q-8fvv
CVE: CVE-2025-54066
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-17
Source: https://github.com/advisories/GHSA-hfj7-542q-8fvv
Type: github-advisory

## Affected
- npm: `@dirac-grid/diracx-web-components` — affected >=0 <0.1.0-a8

## Details
### Summary

An attacker can forge a request to redirect an authenticated user to any arbitrary website.

### Details

On the login page, we have a `redirect` field which is the location where the server will redirect the user. This URI is not verified, and can be an arbitrary URI.

Paired with a parameter pollution, we can hide our malicious URI (ex: `https://dns.com/?param1=im_hidden_if_theres_lot_of_args?param1=bbb`).

### PoC

https://diracx-cert.app.cern.ch/auth?redirect=https://ipcim.com/en/where/?dsdsd=qsqsfsjfnsfniizaeiaapzqlalkqkaizqqijsjaopmqmxna?redirect=https://diracx-cert-app.cern.ch/auth

This POC can leak user's position.

### Impact

This could be used for phishing and extracting new data (such as redirecting to a new "log in" page, and asking users to reenter credentials).

## References
- https://github.com/DIRACGrid/diracx-web/security/advisories/GHSA-hfj7-542q-8fvv
- https://nvd.nist.gov/vuln/detail/CVE-2025-54066
- https://github.com/DIRACGrid/diracx-web/commit/eba3b7bc4f9d394074215986e6d3c15b546b25d5
- https://github.com/DIRACGrid/diracx-web
