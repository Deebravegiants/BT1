# [M] devalue has prototype pollution in devalue.parse and devalue.unflatten

## Summary
Severity: Medium
Advisory: GHSA-cfw5-2vxh-hr84
CVE: CVE-2026-30226
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-cfw5-2vxh-hr84
Type: github-advisory

## Affected
- npm: `devalue` — affected >=0 <5.6.4

## Details
In devalue v5.6.3, `devalue.parse` and `devalue.unflatten` were susceptible to prototype pollution via maliciously crafted payloads. Successful exploitation could lead to Denial of Service (DoS) or type confusion.

## References
- https://github.com/sveltejs/devalue/security/advisories/GHSA-cfw5-2vxh-hr84
- https://nvd.nist.gov/vuln/detail/CVE-2026-30226
- https://github.com/sveltejs/devalue
