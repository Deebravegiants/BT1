# [H] Svelte devalue: DoS via sparse array deserialization

## Summary
Severity: High
Advisory: GHSA-77vg-94rm-hx3p
CVE: CVE-2026-42570
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-77vg-94rm-hx3p
Type: github-advisory

## Affected
- npm: `devalue` — affected >=5.6.3 <5.8.1

## Details
`devalue.parse` could, due to quirks in some JavaScript engines, be convinced to allocate much more memory than was needed when deserializing sparse arrays, leading to excessive memory consumption.

## References
- https://github.com/sveltejs/devalue/security/advisories/GHSA-77vg-94rm-hx3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-42570
- https://github.com/sveltejs/devalue/commit/206ca6712fbc380a4571c59de9ab04b91110792d
- https://github.com/sveltejs/devalue
- https://github.com/sveltejs/devalue/releases/tag/v5.8.1
