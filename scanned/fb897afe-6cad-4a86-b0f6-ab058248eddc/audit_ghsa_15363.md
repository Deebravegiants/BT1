# [M] Nomad Vulnerable to Allocation Directory Escape On Non-Existing File Paths Through Archive Unpacking

## Summary
Severity: Medium
Advisory: GHSA-25qx-vfw2-fw8r
CVE: CVE-2024-7625
CWE: CWE-610
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-15
Source: https://github.com/advisories/GHSA-25qx-vfw2-fw8r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.6.1 <1.6.14
- Go: `github.com/hashicorp/nomad` — affected >=1.7.0 <1.7.11
- Go: `github.com/hashicorp/nomad` — affected >=1.8.0 <1.8.3

## Details
In HashiCorp Nomad and Nomad Enterprise from 0.6.1 up to 1.6.13, 1.7.10, and 1.8.2, the archive unpacking process is vulnerable to writes outside the allocation directory during migration of allocation directories when multiple archive headers target the same file. This vulnerability, CVE-2024-7625, is fixed in Nomad 1.6.14, 1.7.11, and 1.8.3. Access or compromise of the Nomad client agent at the source allocation first is a prerequisite for leveraging this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7625
- https://discuss.hashicorp.com/t/hcsec-2024-17-nomad-vulnerable-to-allocation-directory-escape-on-non-existing-file-paths-through-archive-unpacking/69293
- github.com/hashicorp/nomad
