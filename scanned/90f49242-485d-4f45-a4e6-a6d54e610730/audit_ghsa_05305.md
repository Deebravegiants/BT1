# [M] Canonical MicroCeph: path traversal issue in the remote-import AP

## Summary
Severity: Medium
Advisory: GHSA-xg3j-c7q4-f9ph
CVE: CVE-2026-10720
CWE: CWE-23
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:L/VA:L/SC:N/SI:H/SA:H (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-xg3j-c7q4-f9ph
Type: github-advisory

## Affected
- Go: `github.com/canonical/microceph/microceph` — affected >=0 <0.0.0-20260609072127-5c2760d8fb76

## Details
Canonical MicroCeph versions from the squid and tentacle track are vulnerable to a path traversal issue in the remote-import API. Holders of a trusted cluster mTLS certificate (such as enrolled cluster members) or join token can manipulate files in an imported remote cluster within the /var/snap/microceph confinement. This would allow daemon disruption and pollution of the cluster state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10720
- https://github.com/canonical/microceph/pull/758
- https://github.com/canonical/microceph/commit/5c2760d8fb765d670e2673d3a537b67eae4b67c6
- https://github.com/advisories/GHSA-xg3j-c7q4-f9ph
- https://github.com/canonical/microceph
