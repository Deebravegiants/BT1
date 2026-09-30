# [M] Cube Core is vulnerable to Denial of Service (DoS) via crafted request

## Summary
Severity: Medium
Advisory: GHSA-9vph-2hvm-x66g
CVE: CVE-2026-25957
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-9vph-2hvm-x66g
Type: github-advisory

## Affected
- npm: `@cubejs-backend/server-core` — affected >=1.1.17 <1.4.2
- npm: `@cubejs-backend/server-core` — affected >=1.5.0 <1.5.13

## Details
### **Impact**

It is possible to make the entire Cube API unavailable by submitting a specially crafted request to a Cube API endpoint.

### Affected Versions:

`>= 1.1.17`

### Mitigation:

Upgrade to a patched version:

- 1.5.13 and later (regular release)
- 1.4.2 (active [LTS release](https://cube.dev/docs/product/administration/distribution#long-term-support))

### **References**

The issue was reported by our Core engineer, Dmitrii Patsura (@ovr), in our internal Slack and was promptly patched in a recent update.

## References
- https://github.com/cube-js/cube/security/advisories/GHSA-9vph-2hvm-x66g
- https://nvd.nist.gov/vuln/detail/CVE-2026-25957
- https://github.com/cube-js/cube
