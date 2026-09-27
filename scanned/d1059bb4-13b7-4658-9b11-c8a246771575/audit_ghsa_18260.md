# [H] dref is vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-76g8-235f-gj6p
CVE: CVE-2025-26278
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-76g8-235f-gj6p
Type: github-advisory

## Affected
- npm: `dref` — affected >=0

## Details
A prototype pollution in the lib.set function of dref v0.1.2 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26278
- https://gist.github.com/tariqhawis/ad92d5e683f3a5d83e0629955ff42ad7
- https://github.com/OrangeShieldInfos/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-26278
