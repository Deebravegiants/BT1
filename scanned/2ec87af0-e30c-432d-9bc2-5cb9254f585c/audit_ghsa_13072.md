# [M] Alertmanager UI is vulnerable to stored XSS via the /api/v1/alerts endpoint

## Summary
Severity: Medium
Advisory: GHSA-v86x-5fm3-5p7j
CVE: CVE-2023-40577
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-v86x-5fm3-5p7j
Type: github-advisory

## Affected
- Go: `github.com/prometheus/alertmanager` — affected >=0 <0.25.1

## Details
### Impact

An attacker with the permission to perform POST requests on the /api/v1/alerts endpoint could be able to execute arbitrary JavaScript code on the users of Prometheus Alertmanager.

### Patches

Users can upgrade to Alertmanager v0.2.51.

### Workarounds

Users can setup a reverse proxy in front of the Alertmanager web server to forbid access to the /api/v1/alerts endpoint.

### References

N/A

## References
- https://github.com/prometheus/alertmanager/security/advisories/GHSA-v86x-5fm3-5p7j
- https://nvd.nist.gov/vuln/detail/CVE-2023-40577
- https://github.com/prometheus/alertmanager
- https://lists.debian.org/debian-lts-announce/2023/10/msg00011.html
