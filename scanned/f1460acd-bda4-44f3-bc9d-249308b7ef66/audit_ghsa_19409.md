# [H] Homograph attack allows Unicode lookalike characters to bypass validation.

## Summary
Severity: High
Advisory: GHSA-xq7p-g2vc-g82p
CVE: CVE-2025-27611
CWE: CWE-1007
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-xq7p-g2vc-g82p
Type: github-advisory

## Affected
- npm: `base-x` — affected >=5.0.0 <5.0.1
- npm: `base-x` — affected >=4.0.0 <4.0.1
- npm: `base-x` — affected >=0 <3.0.11

## Details
### Impact

Attackers can deceive users into sending funds to an unintended address.

### Patches

https://github.com/cryptocoinjs/base-x/pull/86

## References
- https://github.com/cryptocoinjs/base-x/security/advisories/GHSA-xq7p-g2vc-g82p
- https://nvd.nist.gov/vuln/detail/CVE-2025-27611
- https://github.com/cryptocoinjs/base-x/pull/86
- https://github.com/cryptocoinjs/base-x
