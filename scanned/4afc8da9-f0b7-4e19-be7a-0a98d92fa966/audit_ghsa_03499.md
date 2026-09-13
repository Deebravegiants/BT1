# [C] Prototype Pollution Vulnerability in object-collider

## Summary
Severity: Critical
Advisory: GHSA-85g2-29m8-qf2p
CVE: CVE-2021-25914
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-85g2-29m8-qf2p
Type: github-advisory

## Affected
- npm: `object-collider` — affected >=1.0.0 <1.0.4

## Details
Prototype pollution vulnerability in 'object-collider' versions 1.0.0 through 1.0.3 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25914
- https://github.com/FireBlinkLTD/object-collider/commit/321f75a7f8e7b3393e5b7dd6dd9ab26ede5906e5
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25914
