# [C] Prototype Pollution in vm2

## Summary
Severity: Critical
Advisory: GHSA-rjf2-j2r6-q8gr
CVE: CVE-2021-23449
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-rjf2-j2r6-q8gr
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.9.4

## Details
This affects the package vm2 before 3.9.4. Prototype Pollution attack vector can lead to sandbox escape and execution of arbitrary code on the host machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23449
- https://github.com/patriksimek/vm2/issues/363
- https://github.com/patriksimek/vm2/commit/b4f6e2bd2c4a1ef52fc4483d8e35f28bc4481886
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.9.4
- https://security.netapp.com/advisory/ntap-20211029-0010
- https://snyk.io/vuln/SNYK-JS-VM2-1585918
