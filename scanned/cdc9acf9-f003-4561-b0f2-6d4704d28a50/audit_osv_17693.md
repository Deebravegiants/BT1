# [C] CVE-2020-1911

## Summary
Severity: Critical
Advisory: CVE-2020-1911
Aliases: GHSA-f5x2-xv93-4p23
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-04
Source: https://osv.dev/vulnerability/CVE-2020-1911
Type: osv

## Details
A type confusion vulnerability when resolving properties of JavaScript objects with specially-crafted prototype chains in Facebook Hermes prior to commit fe52854cdf6725c2eaa9e125995da76e6ceb27da allows attackers to potentially execute arbitrary code via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://www.facebook.com/security/advisories/cve-2020-1911
- https://github.com/facebook/hermes/commit/fe52854cdf6725c2eaa9e125995da76e6ceb27da
