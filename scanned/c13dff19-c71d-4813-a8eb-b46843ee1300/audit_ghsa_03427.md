# [M] Improper Neutralization of Input in Theia console

## Summary
Severity: Medium
Advisory: GHSA-cwg9-c9cr-p5fq
CVE: CVE-2021-28161
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-cwg9-c9cr-p5fq
Type: github-advisory

## Affected
- npm: `@theia/console` — affected >=0 <1.8.1

## Details
In Eclipse Theia versions up to and including 1.8.0, in the debug console there is no HTML escaping, so arbitrary Javascript code can be injected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28161
- https://github.com/eclipse-theia/theia/issues/8794
