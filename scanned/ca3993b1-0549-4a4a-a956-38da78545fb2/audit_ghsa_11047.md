# [H] Grafana Tempo has Inadequate Encryption Strength

## Summary
Severity: High
Advisory: GHSA-ffqx-q65f-36jf
CVE: CVE-2026-28377
CWE: CWE-326
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-ffqx-q65f-36jf
Type: github-advisory

## Affected
- Go: `github.com/grafana/tempo` — affected >=0 <2.10.3

## Details
A vulnerability in Grafana Tempo exposes the S3 SSE-C encryption key in plaintext through the /status/config endpoint, potentially allowing unauthorized users to obtain the key used to encrypt trace data stored in S3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28377
- https://github.com/grafana/tempo/commit/bb8ca663db34a0980c9758b40d918fda3b4dbec3
- https://github.com/advisories/GHSA-ffqx-q65f-36jf
- https://github.com/grafana/tempo
- https://github.com/grafana/tempo/blob/4dc3e5b0d3463a0b67498b662b85a148698b4afd/CHANGELOG.md?plain=1#L135
- https://grafana.com/security/security-advisories/cve-2026-28377
