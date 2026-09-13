# [H] HashiCorp Nomad vulnerable to symlink attacks

## Summary
Severity: High
Advisory: GHSA-c866-8gpw-p3mv
CVE: CVE-2024-1329
CWE: CWE-59, CWE-610
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-c866-8gpw-p3mv
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.5.13 <1.5.14
- Go: `github.com/hashicorp/nomad` — affected >=1.6.0 <1.6.7
- Go: `github.com/hashicorp/nomad` — affected >=1.7.3 <1.7.4

## Details
HashiCorp Nomad and Nomad Enterprise 1.5.13 up to 1.6.6, and 1.7.3 template renderer is vulnerable to arbitrary file write on the host as the Nomad client user through symlink attacks. Fixed in Nomad 1.7.4, 1.6.7, 1.5.14.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1329
- https://github.com/hashicorp/nomad/issues/19888
- https://github.com/hashicorp/nomad/commit/b3209cbc6921e703b0e9984ce70c10b378665834
- https://github.com/hashicorp/nomad/commit/d1721c7a6fc1833778086603f818a822a34f445a
- https://github.com/hashicorp/nomad/commit/de55da677a21ac7572c0f4a8cd9abd5473c47a70
- https://discuss.hashicorp.com/t/hcsec-2024-03-nomad-vulnerable-to-arbitrary-write-through-symlink-attack
- https://github.com/hashicorp/nomad
