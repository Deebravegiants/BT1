# [H] @tanstack/form-core prototype pollution

## Summary
Severity: High
Advisory: GHSA-ggv3-vmgw-xv2q
CVE: CVE-2024-57068
CWE: CWE-732
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-ggv3-vmgw-xv2q
Type: github-advisory

## Affected
- npm: `@tanstack/form-core` — affected >=0 <0.42.1

## Details
A prototype pollution in the lib.mutateMergeDeep function of @tanstack/form-core v0.35.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57068
- https://github.com/TanStack/form/pull/1151
- https://github.com/TanStack/form/commit/455522c8f3272787668f3d1afd6adbc6dc1b9e8a
- https://gist.github.com/tariqhawis/47fe5b1e584e9e573c0933588248d533
- https://github.com/TanStack/form
