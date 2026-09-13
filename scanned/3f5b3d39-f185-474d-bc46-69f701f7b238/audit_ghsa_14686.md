# [M] Hashicorp Nomad Incorrect Privilege Assignment vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hr68-hvgv-xxqf
CVE: CVE-2024-12678
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-hr68-hvgv-xxqf
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <1.9.4

## Details
Nomad Community and Nomad Enterprise ("Nomad") allocations are vulnerable to privilege escalation within a namespace through unredacted workload identity tokens. This vulnerability, identified as CVE-2024-12678, is fixed in Nomad Community Edition 1.9.4 and Nomad Enterprise 1.9.4, 1.8.8, and 1.7.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12678
- https://github.com/hashicorp/nomad/commit/359a71861ef044cb5d749a36ff0e44b172c8f1a6
- https://discuss.hashicorp.com/t/hcsec-2024-29-nomad-allocations-vulnerable-to-privilege-escalation-within-a-namespace-using-unredacted-workload-identity-token/72119
- https://github.com/hashicorp/nomad
