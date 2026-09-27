# [H] Prototype Pollution in NASA Open MCT

## Summary
Severity: High
Advisory: GHSA-4xcx-cwrq-w792
CVE: CVE-2023-45282
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-4xcx-cwrq-w792
Type: github-advisory

## Affected
- npm: `openmct` — affected >=0

## Details
In NASA Open MCT (aka openmct) before commit 545a177 is subject to a prototype pollution which can occur via an import action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45282
- https://github.com/nasa/openmct/pull/7094/commits/545a1770c523ecc3410dca884c6809d5ff0f9d52
- https://github.com/nasa/openmct/commit/2243381d527c0d84cc48e9ace78be7cda5363612
- https://github.com/nasa/openmct
- https://github.com/nasa/openmct/compare/v3.0.2...v3.1.0
- https://nasa.github.io/openmct
- https://www.linkedin.com/pulse/prototype-pollution-nasas-open-mct-cve-2023-45282
