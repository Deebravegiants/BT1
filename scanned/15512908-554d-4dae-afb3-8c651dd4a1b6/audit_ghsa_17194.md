# [C] @thi.ng/paths Prototype Pollution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8ppr-www8-hfjx
CVE: CVE-2024-29650
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-8ppr-www8-hfjx
Type: github-advisory

## Affected
- npm: `@thi.ng/paths` — affected >=0 <5.1.63

## Details
An issue in @thi.ng/paths v.5.1.62 and before allows a remote attacker to execute arbitrary code via the `mutIn` and `mutInManyUnsafe` components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29650
- https://github.com/thi-ng/umbrella/issues/445
- https://github.com/thi-ng/umbrella/commit/c78b484882ad5214a46ef83ddb8020571c171353
- https://gist.github.com/tariqhawis/1bc340ca5ea6ae115c9ab9665cfd5921
- https://github.com/thi-ng/umbrella
- https://learn.snyk.io/lesson/prototype-pollution/#a0a863a5-fd3a-539f-e1ed-a0769f6c6e3b
