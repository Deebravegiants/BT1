# [H] Use of Potentially Dangerous Function in mixme

## Summary
Severity: High
Advisory: GHSA-79jw-6wg7-r9g4
CVE: CVE-2021-29491
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-79jw-6wg7-r9g4
Type: github-advisory

## Affected
- npm: `mixme` — affected >=0 <0.5.1

## Details
### Impact

In Node.js mixme v0.5.0, an attacker can add or alter properties of an object via 'proto' through the mutate() and merge() functions. The polluted attribute will be directly assigned to every object in the program. This will put the availability of the program at risk causing a potential denial of service (DoS).

### Patches
The problem is corrected starting with version 0.5.1.

### References
Issue: https://github.com/adaltas/node-mixme/issues/1
Commit: https://github.com/adaltas/node-mixme/commit/cfd5fbfc32368bcf7e06d1c5985ea60e34cd4028

## References
- https://github.com/adaltas/node-mixme/security/advisories/GHSA-79jw-6wg7-r9g4
- https://nvd.nist.gov/vuln/detail/CVE-2021-29491
- https://security.netapp.com/advisory/ntap-20210622-0002
