# [H] HashiCorp Nomad vulnerable to a path traversal

## Summary
Severity: High
Advisory: GHSA-hx53-77qj-8663
CVE: CVE-2026-7474
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-hx53-77qj-8663
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <1.11.0-rc.1.0.20260511152149-cd7240c4099a

## Details
HashiCorp Nomad and Nomad Enterprise prior to 2.0.1 are vulnerable to code execution on the client host through a path traversal attack. This vulnerability (CVE-2026-7474) is fixed in Nomad 2.0.1, 1.11.5 and 1.10.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7474
- https://github.com/hashicorp/nomad/commit/cd7240c4099ad33eda279924fb3a9459b162d120
- https://discuss.hashicorp.com/t/hcsec-2026-15-nomad-vulnerable-to-path-traversal-in-dynamic-host-volume-which-may-lead-to-code-execution/77417
- https://github.com/hashicorp/nomad
- https://github.com/hashicorp/nomad/releases/tag/v2.0.1
