# [M] Grafana Tempo vulnerable to an out-of-memory crash

## Summary
Severity: Medium
Advisory: GHSA-6xff-cpcq-vpw2
CVE: CVE-2026-27878
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6xff-cpcq-vpw2
Type: github-advisory

## Affected
- Go: `github.com/grafana/tempo` — affected >=0 <1.5.1-0.20260303204923-b13f74291d48

## Details
A TraceQL query in Grafana Tempo with a large exemplars hint value can cause the Tempo instance to allocate an excessive amount of memory, resulting in an out-of-memory crash. This could allow an authenticated user to trigger a denial of service against the Tempo service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27878
- https://github.com/grafana/tempo/pull/6559
- https://github.com/grafana/tempo/pull/6646
- https://github.com/grafana/tempo/pull/6792
- https://github.com/grafana/tempo/pull/6802
- https://github.com/grafana/tempo/commit/3d7c78d438890991df594c20ae2031f8934aba3b
- https://github.com/grafana/tempo/commit/b13f74291d489672601a10297f8fbcbf7dd19192
- https://github.com/grafana/tempo/commit/b481ae9693f99785691197915066e6306950fa09
- https://github.com/grafana/tempo/commit/e2d51b786aff94de3319c07994c6a5539b121eb5
- https://github.com/grafana/tempo
- https://github.com/grafana/tempo/releases/tag/v2.10.2
- https://github.com/grafana/tempo/releases/tag/v2.8.4
- https://github.com/grafana/tempo/releases/tag/v2.9.2
- https://grafana.com/security/security-advisories/cve-2026-27878
