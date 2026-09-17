# [M] HashiCorp Nomad vulnerable to non-sensitive metadata exposure

## Summary
Severity: Medium
Advisory: GHSA-7wg4-8m5p-hrfg
CVE: CVE-2022-3866
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-7wg4-8m5p-hrfg
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.4.0 <1.4.2

## Details
HashiCorp Nomad and Nomad Enterprise 1.4.0 up to 1.4.1 workload identity token can list non-sensitive metadata for paths under `nomad/` that belong to other jobs in the same namespace. Fixed in 1.4.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3866
- https://github.com/hashicorp/nomad/commit/3b24f26603e2b116ba324101afa8a7e3a7a769a5
- https://discuss.hashicorp.com/t/hcsec-2022-25-nomad-s-workload-identity-token-can-list-non-sensitive-metadata-for-nomad-paths/46167
- https://github.com/hashicorp/nomad
