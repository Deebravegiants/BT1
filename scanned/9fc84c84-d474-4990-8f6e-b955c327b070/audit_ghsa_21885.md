# [C] Prototype Pollution in mixme

## Summary
Severity: Critical
Advisory: GHSA-r5cq-9537-9rpf
CVE: CVE-2021-28860
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-r5cq-9537-9rpf
Type: github-advisory

## Affected
- npm: `mixme` — affected >=0 <0.5.1

## Details
Node.js mixme 0.5.0, an attacker can add or alter properties of an object via '__proto__' through the mutate() and merge() functions. The polluted attribute will be directly assigned to every object in the program. This will put the availability of the program at risk causing a potential denial of service (DoS).

## References
- https://github.com/adaltas/node-mixme/security/advisories/GHSA-79jw-6wg7-r9g4
- https://nvd.nist.gov/vuln/detail/CVE-2021-28860
- https://github.com/adaltas/node-mixme/issues/1
- https://github.com/adaltas/node-mixme/commit/cfd5fbfc32368bcf7e06d1c5985ea60e34cd4028
- https://github.com/adaltas/node-mixme
- https://security.netapp.com/advisory/ntap-20210618-0005
- https://www.npmjs.com/~david
- http://nodejs.com
