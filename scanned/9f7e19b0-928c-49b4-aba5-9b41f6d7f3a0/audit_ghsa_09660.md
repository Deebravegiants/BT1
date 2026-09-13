# [C] Pyroscope Exposes Storage Secret

## Summary
Severity: Critical
Advisory: GHSA-m9hq-h476-h2g8
CVE: CVE-2025-41118
CWE: CWE-200, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-m9hq-h476-h2g8
Type: github-advisory

## Affected
- Go: `github.com/grafana/pyroscope` — affected >=0 <1.15.2
- Go: `github.com/grafana/pyroscope` — affected >=1.16.0 <1.16.1

## Details
Pyroscope is an open-source continuous profiling database. The database supports various storage backends, including Tencent Cloud Object Storage (COS).

If the database is configured to use Tencent COS as the storage backend, an attacker could extract the secret_key configuration value from the Pyroscope API.

To exploit this vulnerability, an attacker needs direct access to the Pyroscope API. We highly recommend limiting the public internet exposure of all our databases, such that they are only accessible by trusted users or internal systems.

This vulnerability is fixed in versions:

1.15.x: 1.15.2 and above.
1.16.x: 1.16.1 and above.
1.17.x: 1.17.0 and above (i.e. all versions).

Thanks to Théo Cusnir for reporting this vulnerability to us via our bug bounty program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41118
- https://github.com/grafana/pyroscope
- https://grafana.com/security/security-advisories/cve-2025-41118
