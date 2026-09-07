# [M] Golang protojson.Unmarshal function infinite loop when unmarshaling certain forms of invalid JSON

## Summary
Severity: Medium
Advisory: GHSA-8r3f-844c-mc37
CVE: CVE-2024-24786
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-8r3f-844c-mc37
Type: github-advisory

## Affected
- Go: `google.golang.org/protobuf` — affected >=0 <1.33.0
- Go: `google.golang.org/protobuf/encoding/protojson` — affected >=0 <1.33.0
- Go: `google.golang.org/protobuf/internal/encoding/json` — affected >=0 <1.33.0

## Details
The protojson.Unmarshal function can enter an infinite loop when unmarshaling certain forms of invalid JSON. This condition can occur when unmarshaling into a message which contains a google.protobuf.Any value, or when the UnmarshalOptions.DiscardUnknown option is set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24786
- https://github.com/protocolbuffers/protobuf-go/commit/f01a588e5810b90996452eec4a28f22a0afae023
- https://github.com/protocolbuffers/protobuf-go
- https://github.com/protocolbuffers/protobuf-go/releases/tag/v1.33.0
- https://go.dev/cl/569356
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JDMBHAVSDU2FBDZ45U3A2VLSM35OJ2HU
- https://pkg.go.dev/vuln/GO-2024-2611
- https://security.netapp.com/advisory/ntap-20240517-0002
- http://www.openwall.com/lists/oss-security/2024/03/08/4
