# [M] free5GC vulnerable to malformed NGAP message crashing the AMF and NGAP decoders

## Summary
Severity: Medium
Advisory: GHSA-59hj-62f5-fgmc
CVE: CVE-2022-43677
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-24
Source: https://github.com/advisories/GHSA-59hj-62f5-fgmc
Type: github-advisory

## Affected
- Go: `github.com/free5gc/free5gc` — affected >=0

## Details
In free5GC 3.2.1, a malformed NGAP message can crash the AMF and NGAP decoders via an index-out-of-range panic in `aper.GetBitString`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43677
- https://github.com/free5gc/free5gc/issues/402
- https://github.com/free5gc/free5gc
- https://pkg.go.dev/vuln/GO-2022-1083
