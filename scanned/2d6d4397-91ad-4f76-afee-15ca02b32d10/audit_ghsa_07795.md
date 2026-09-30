# [H] Cube Core is vulnerable to privilege escalation via a specially crafted request

## Summary
Severity: High
Advisory: GHSA-v226-32c7-x2v7
CVE: CVE-2026-25958
CWE: CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-v226-32c7-x2v7
Type: github-advisory

## Affected
- npm: `@cubejs-backend/server-core` — affected >=0.27.19 <1.0.14
- npm: `@cubejs-backend/server-core` — affected >=1.1.0 <1.4.2
- npm: `@cubejs-backend/server-core` — affected >=1.5.0 <1.5.13

## Details
### **Impact**

It is possible to make a specially crafted request with a valid API token that leads to privilege escalation.

### Affected Versions:

`≥= 0.27.19` 

### Mitigation:

Upgrade to a patched version:

- 1.5.13 and later (regular release)
- 1.4.2 (active [LTS release](https://cube.dev/docs/product/administration/distribution#long-term-support))
- 1.0.14 (end-of-life LTS release)

### **References**

The issue was reported by our Core engineer, Dmitrii Patsura (@ovr), in our internal Slack and was promptly patched in a recent update.

## References
- https://github.com/cube-js/cube/security/advisories/GHSA-v226-32c7-x2v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25958
- https://github.com/cube-js/cube
