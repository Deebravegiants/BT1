# [C] pgx contains memory-safety vulnerability

## Summary
Severity: Critical
Advisory: GHSA-xgrm-4fwx-7qm8
CVE: CVE-2026-33815
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-xgrm-4fwx-7qm8
Type: github-advisory

## Affected
- Go: `github.com/jackc/pgx/v5` — affected >=0 <5.9.0

## Details
[pgx](github.com/jackc/pgx/v5) is a pure Go driver and toolkit for PostgreSQL. pgx prior to v5.9.0 contains a memory-safety vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33815
- https://github.com/jackc/pgx/issues/2519
- https://github.com/jackc/pgx/issues/2530
- https://github.com/jackc/pgx/commit/6dbad4cafdb8a4daab7ff79c858c95da4b6109e8
- https://pkg.go.dev/vuln/GO-2026-4771
- github.com/jackc/pgx/v5
