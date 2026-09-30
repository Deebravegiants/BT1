# [M] Uncontrolled Resource Consumption in Hashicorp Nomad

## Summary
Severity: Medium
Advisory: GHSA-w479-w22g-cffh
CVE: CVE-2023-0821
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-17
Source: https://github.com/advisories/GHSA-w479-w22g-cffh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.2.15 <1.2.16
- Go: `github.com/hashicorp/nomad` — affected >=1.3.0 <1.3.9
- Go: `github.com/hashicorp/nomad` — affected >=1.4.0 <1.4.4

## Details
HashiCorp Nomad and Nomad Enterprise 1.2.15 up to 1.3.8, and 1.4.3 jobs using a maliciously compressed artifact stanza source can cause excessive disk usage. Fixed in 1.2.16, 1.3.9, and 1.4.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0821
- https://discuss.hashicorp.com/t/hcsec-2023-05-nomad-client-vulnerable-to-decompression-bombs-in-artifact-block/50292
