# [M] Nomad is vulnerable to unintentional exposure of the workload identity token and client secret token in audit logs

## Summary
Severity: Medium
Advisory: GHSA-c3q9-q986-vrwh
CVE: CVE-2025-1296
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-c3q9-q986-vrwh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0

## Details
Nomad Community and Nomad Enterprise (“Nomad”) are vulnerable to unintentional exposure of the workload identity token and client secret token in audit logs. This vulnerability, identified as CVE-2025-1296, is fixed in Nomad Community Edition 1.9.7 and Nomad Enterprise 1.9.7, 1.8.11, and 1.7.19.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1296
- https://github.com/hashicorp/nomad/commit/dc482bf9058faf7a192486eb52caa1d42646f6b3
- https://discuss.hashicorp.com/t/hcsec-2025-04-nomad-exposes-sensitive-workload-identity-and-client-secret-token-in-audit-logs/73737
- https://github.com/hashicorp/nomad
- https://pkg.go.dev/vuln/GO-2025-3510
