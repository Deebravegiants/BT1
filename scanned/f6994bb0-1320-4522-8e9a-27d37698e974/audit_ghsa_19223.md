# [M] Linkerd resource exhaustion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-42mr-jpwh-m9rv
CVE: CVE-2025-43915
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-42mr-jpwh-m9rv
Type: github-advisory

## Affected
- Go: `github.com/linkerd/linkerd2` — affected >=0 <0.0.0-20250212165942-faa3f617eef5

## Details
In Linkerd edge releases before edge-25.2.1, and Buoyant Enterprise for Linkerd releases 2.13.0–2.13.7, 2.14.0–2.14.10, 2.15.0–2.15.7, 2.16.0–2.16.4, and 2.17.0–2.17.1, resource exhaustion can occur for Linkerd proxy metrics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43915
- https://docs.buoyant.io/security/advisories/2025-01
- https://github.com/linkerd/linkerd2
- https://pkg.go.dev/vuln/GO-2025-3664
- https://www.buoyant.io/resources
