# [H] Grafana Tempo has an Uncontrolled Resource Consumption issue

## Summary
Severity: High
Advisory: GHSA-p4r4-xvrq-gvmc
CVE: CVE-2026-21728
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-p4r4-xvrq-gvmc
Type: github-advisory

## Affected
- Go: `github.com/grafana/tempo` — affected >=1.3.0 <2.8.4
- Go: `github.com/grafana/tempo` — affected >=2.9.0 <2.9.2
- Go: `github.com/grafana/tempo` — affected >=2.10.0 <2.10.2

## Details
Tempo queries with large limits can cause large memory allocations which can impact the availability of the service, depending on its deployment strategy.

Mitigation can be done by setting max_result_limit in the search config, e.g. to 262144 (2^18).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-21728
- https://github.com/grafana/tempo/pull/6525
- https://github.com/grafana/tempo/commit/650eb1985a0776789c8564122990f588a742356f
- https://github.com/grafana/tempo
- https://github.com/grafana/tempo/blob/4dc3e5b0d3463a0b67498b662b85a148698b4afd/docs/sources/tempo/release-notes/version-2/v2-10.md?plain=1#L328
- https://github.com/grafana/tempo/blob/4dc3e5b0d3463a0b67498b662b85a148698b4afd/docs/sources/tempo/release-notes/version-2/v2-8.md?plain=1#L251
- https://github.com/grafana/tempo/blob/4dc3e5b0d3463a0b67498b662b85a148698b4afd/docs/sources/tempo/release-notes/version-2/v2-9.md?plain=1#L224
- https://grafana.com/security/security-advisories/cve-2026-21728
