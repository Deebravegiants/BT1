# [M] onos-lib-go allows an index out-of-range panic

## Summary
Severity: Medium
Advisory: GHSA-jrqj-6vq2-7r63
CVE: CVE-2025-30077
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-16
Source: https://github.com/advisories/GHSA-jrqj-6vq2-7r63
Type: github-advisory

## Affected
- Go: `github.com/onosproject/onos-lib-go` — affected >=0

## Details
Open Networking Foundation SD-RAN ONOS onos-lib-go 0.10.28 allows an index out-of-range panic in asn1/aper GetBitString via a zero value of numBits.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30077
- https://github.com/onosproject/onos-lib-go/issues/295
- https://github.com/onosproject/onos-lib-go/commit/55579ffad35f59a5945c7861d944cd57a3b4b3d0
- https://github.com/onosproject/onos-lib-go
