# [C] objection.js Prototype Pollution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-r659-8xfp-j327
CVE: CVE-2021-3766
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-r659-8xfp-j327
Type: github-advisory

## Affected
- npm: `objection` — affected >=0 <2.2.16

## Details
objection.js prior to version 2.2.16 is vulnerable to Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution'). This issue is patched in version 2.2.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3766
- https://github.com/Vincit/objection.js/commit/46b842a6bc897198b83f41ac85c92864b991d7e9
- https://github.com/vincit/objection.js/commit/b41aab8dcd78f426f7468dcda541a7aca18a66a6
- https://github.com/vincit/objection.js
- https://huntr.dev/bounties/c98e0f0e-ebf2-4072-be73-a1848ea031cc
