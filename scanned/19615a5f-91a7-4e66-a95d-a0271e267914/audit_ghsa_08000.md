# [M] mongo-go-driver has Heap Out-of-Bounds Read in GSSAPI Error Handling

## Summary
Severity: Medium
Advisory: GHSA-cp6g-7hqx-qxhp
CVE: CVE-2026-2303
CWE: CWE-183
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-cp6g-7hqx-qxhp
Type: github-advisory

## Affected
- Go: `go.mongodb.org/mongo-driver` — affected >=0 <1.17.7
- Go: `go.mongodb.org/mongo-driver/v2` — affected >=0 <2.4.2

## Details
The mongo-go-driver repository contains CGo bindings for GSSAPI (Kerberos) authentication on Linux and macOS. The C wrapper implementation contains a heap out-of-bounds read vulnerability due to incorrect assumptions about string termination in the GSSAPI standard. Since GSSAPI buffers are not guaranteed to be null-terminated or have extra padding, this results in reading one byte past the allocated heap buffer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2303
- https://github.com/mongodb/mongo-go-driver
- https://jira.mongodb.org/browse/GODRIVER-3770
