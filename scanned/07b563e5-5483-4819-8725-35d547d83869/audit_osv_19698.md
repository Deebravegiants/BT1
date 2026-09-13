# [C] CVE-2021-24045

## Summary
Severity: Critical
Advisory: CVE-2021-24045
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-13
Source: https://osv.dev/vulnerability/CVE-2021-24045
Type: osv

## Details
A type confusion vulnerability could be triggered when resolving the "typeof" unary operator in Facebook Hermes prior to v0.10.0. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://www.facebook.com/security/advisories/cve-2021-24045
- https://github.com/facebook/hermes/commit/55e1b2343f4deb1a1b5726cfe1e23b2068217ff2
