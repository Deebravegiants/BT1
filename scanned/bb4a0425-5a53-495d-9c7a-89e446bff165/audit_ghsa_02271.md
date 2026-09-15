# [M] Unlimited transforms allowed for signed nodes

## Summary
Severity: Medium
Advisory: GHSA-5379-r78w-42h2
CVE: CVE-2021-39171
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-5379-r78w-42h2
Type: github-advisory

## Affected
- npm: `passport-saml` — affected >=0 <3.1.0

## Details
### Impact
A malicious SAML payload can require transforms that consume significant system resources to process, thereby resulting in reduced or denied service. This would be an effective way to perform a denial-of-service attack.

### Patches
This has been resolved in version 3.1.0. The resolution is to limit the number of allowable transforms to 2.

### References
https://github.com/node-saml/passport-saml/pull/595

## References
- https://github.com/node-saml/passport-saml/security/advisories/GHSA-5379-r78w-42h2
- https://nvd.nist.gov/vuln/detail/CVE-2021-39171
- https://github.com/node-saml/passport-saml/pull/595
- https://github.com/node-saml/passport-saml/commit/f1e00b64c21a725f545e675cd810bbaa435a3972
- https://github.com/node-saml/passport-saml
