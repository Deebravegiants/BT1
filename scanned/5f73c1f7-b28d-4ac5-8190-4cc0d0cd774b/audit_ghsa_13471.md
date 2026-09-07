# [H] DoS vulnerability for apps with sockets enabled

## Summary
Severity: High
Advisory: GHSA-gpw9-fwm8-7rx7
CVE: CVE-2023-38504
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-27
Source: https://github.com/advisories/GHSA-gpw9-fwm8-7rx7
Type: github-advisory

## Affected
- npm: `sails` — affected >=0 <1.5.7

## Details
### Impact
In Sails apps <=v1.5.6, an attacker can send a virtual request that will cause the node process to crash. 

### Patches
This behavior was fixed in Sails [v1.5.7](https://github.com/balderdashy/sails/releases/tag/v1.5.7)

### Workarounds
Disable the sockets hook and remove the `sails.io.js` client

### References
https://github.com/balderdashy/sails/pull/7287

Big thanks to @ThomasRinsma at [Codean](https://www.linkedin.com/company/codeanio/)!

## References
- https://github.com/balderdashy/sails/security/advisories/GHSA-gpw9-fwm8-7rx7
- https://nvd.nist.gov/vuln/detail/CVE-2023-38504
- https://github.com/balderdashy/sails/pull/7287
- https://github.com/balderdashy/sails/commit/4a023dc5095a4b30fdc8535f705ed34cd22d2f7d
- https://github.com/balderdashy/sails
- https://github.com/balderdashy/sails/releases/tag/v1.5.7
