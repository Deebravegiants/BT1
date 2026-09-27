# [H] @ndhoule/defaults prototype pollution

## Summary
Severity: High
Advisory: GHSA-79h2-v6hh-wq23
CVE: CVE-2024-57066
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-79h2-v6hh-wq23
Type: github-advisory

## Affected
- npm: `@ndhoule/defaults` — affected >=0

## Details
A prototype pollution in the lib.deep function of @ndhoule/defaults v2.0.1 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57066
- https://gist.github.com/tariqhawis/8ee7327cc8b78df738cd32505cbbbd44
- https://github.com/ndhoule/defaults
