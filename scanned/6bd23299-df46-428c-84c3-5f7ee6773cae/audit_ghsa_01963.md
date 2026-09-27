# [C] Prototype pollution in safe-flat

## Summary
Severity: Critical
Advisory: GHSA-33rv-m2gp-mm2r
CVE: CVE-2021-25927
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-33rv-m2gp-mm2r
Type: github-advisory

## Affected
- npm: `safe-flat` — affected >=2.0.0 <2.0.2

## Details
Prototype pollution vulnerability in 'safe-flat' versions 2.0.0 through 2.0.1 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25927
- https://github.com/jessie-codes/safe-flat/commit/4b9b7db976bba8c968354f4315f5f9c219b7cbf3
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25927
