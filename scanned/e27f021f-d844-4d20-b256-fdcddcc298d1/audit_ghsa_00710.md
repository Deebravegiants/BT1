# [C] Validation Bypass in schema-inspector

## Summary
Severity: Critical
Advisory: GHSA-r24h-634p-m72x
CVE: CVE-2019-10781
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-r24h-634p-m72x
Type: github-advisory

## Affected
- npm: `schema-inspector` — affected >=0 <1.6.9

## Details
In schema-inspector before 1.6.9, a maliciously crafted JavaScript object can bypass the `sanitize()` and the `validate()` function used within schema-inspector.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10781
- https://github.com/Atinux/schema-inspector/commit/345a7b2eed11bb6128421150d65f4f83fdbb737d
- https://github.com/Atinux/schema-inspector
- https://snyk.io/vuln/SNYK-JS-SCHEMAINSPECTOR-536970
