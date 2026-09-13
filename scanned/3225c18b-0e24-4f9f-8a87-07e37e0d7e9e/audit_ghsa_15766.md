# [H] HashiCorp Nomad is vulnerable to path escape through archive unpacking during migration

## Summary
Severity: High
Advisory: GHSA-5mqx-rpxv-mvxj
CVE: CVE-2024-6717
CWE: CWE-610
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-23
Source: https://github.com/advisories/GHSA-5mqx-rpxv-mvxj
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <1.8.2

## Details
HashiCorp Nomad and Nomad Enterprise 1.6.12 up to 1.7.9, and 1.8.1 archive unpacking during migration is vulnerable to path escaping of the allocation directory. This vulnerability, CVE-2024-6717, is fixed in Nomad 1.6.13, 1.7.10, and 1.8.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6717
- https://github.com/hashicorp/nomad/commit/ef6cdec8847e0698d386d1fd3761743df758ef99
- https://discuss.hashicorp.com/t/hcsec-2024-15-nomad-vulnerable-to-allocation-directory-path-escape-through-archive-unpacking/68781
- https://github.com/hashicorp/nomad
- https://github.com/hashicorp/nomad/releases/tag/v1.8.2
