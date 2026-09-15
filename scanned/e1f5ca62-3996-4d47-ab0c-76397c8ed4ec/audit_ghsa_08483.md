# [M] GoBGP has Improper Restriction of Operations within the Bounds of a Memory Buffer

## Summary
Severity: Medium
Advisory: GHSA-w88c-9vg8-cmq8
CVE: CVE-2026-7737
CWE: CWE-119
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-w88c-9vg8-cmq8
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp` — affected >=0 <4.4.0

## Details
A vulnerability was identified in osrg GoBGP up to 4.3.0. Affected by this issue is the function BMPPeerUpNotification.ParseBody/BMPStatisticsReport.ParseBody of the file pkg/packet/bmp/bmp.go of the component BMP Parser. The manipulation leads to out-of-bounds read. The attack can be initiated remotely. Upgrading to version 4.4.0 can resolve this issue. The identifier of the patch is bc77597d42335c78464bc8e15a471d887bbdf260. Upgrading the affected component is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7737
- https://github.com/osrg/gobgp/commit/bc77597d42335c78464bc8e15a471d887bbdf260
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/releases/tag/v4.4.0
- https://vuldb.com/submit/807605
- https://vuldb.com/vuln/360912
- https://vuldb.com/vuln/360912/cti
