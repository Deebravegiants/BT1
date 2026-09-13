# [M] Insertion of Sensitive Information into Log File in Hashicorp go-getter

## Summary
Severity: Medium
Advisory: GHSA-27rq-4943-qcwp
CVE: CVE-2022-29810
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-27rq-4943-qcwp
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-getter` — affected >=0 <1.5.11

## Details
The Hashicorp go-getter library before 1.5.11 could write SSH credentials into its logfile, exposing sensitive credentials to local users able to read the logfile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29810
- https://github.com/hashicorp/go-getter/pull/348
- https://github.com/hashicorp/go-getter/commit/36b68b2f68a3ed10ee7ecbb0cb9f6b1dc5da49cc
- https://github.com/hashicorp/go-getter
- https://github.com/hashicorp/go-getter/releases/tag/v1.5.11
- https://pkg.go.dev/vuln/GO-2022-0438
