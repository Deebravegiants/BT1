# [H] Unauthenticated Miniflux user can bypass allowed networks check to obtain Prometheus metrics

## Summary
Severity: High
Advisory: GHSA-3qjf-qh38-x73v
CVE: CVE-2023-27591
CWE: CWE-1220, CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-3qjf-qh38-x73v
Type: github-advisory

## Affected
- Go: `miniflux.app/v2` — affected >=0 <2.0.43
- Go: `miniflux.app` — affected >=0

## Details
### Impact

An unauthenticated user can retrieve Prometheus metrics from a publicly reachable Miniflux instance where the `METRICS_COLLECTOR` [configuration option](https://miniflux.app/docs/configuration.html#metrics-collector) is enabled and `METRICS_ALLOWED_NETWORKS` is set to `127.0.0.1/8` (the default).

### Patches

PR #1745 fixes the problem. Available in Miniflux >= 2.0.43.

### Workarounds

Set `METRICS_COLLECTOR` to `false` (default) or run Miniflux behind a trusted reverse-proxy.

### References

- https://miniflux.app/docs/configuration.html#metrics-collector
- https://miniflux.app/docs/configuration.html#metrics-allowed-networks

## References
- https://github.com/miniflux/v2/security/advisories/GHSA-3qjf-qh38-x73v
- https://nvd.nist.gov/vuln/detail/CVE-2023-27591
- https://github.com/miniflux/v2/pull/1745
- https://github.com/miniflux/v2
- https://github.com/miniflux/v2/releases/tag/2.0.43
- https://miniflux.app/docs/configuration.html#metrics-collector
