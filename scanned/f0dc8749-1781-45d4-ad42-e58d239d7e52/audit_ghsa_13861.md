# [M] Panic during unmarshal of Hello Verify Request in github.com/pion/dtls/v2

## Summary
Severity: Medium
Advisory: GHSA-4xgv-j62q-h3rj
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-4xgv-j62q-h3rj
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls` — affected >=0
- Go: `github.com/pion/dtls/v2` — affected >=0 <2.2.4

## Details
### Impact

During the unmarshalling of a hello verify request we could try to unmarshal into too small a buffer. is could result in a panic leading the program to crash.

This issue could be abused to cause a denial of service.

### Workaround

None, upgrade to 2.2.4

## References
- https://github.com/pion/dtls/security/advisories/GHSA-4xgv-j62q-h3rj
- https://github.com/pion/dtls/commit/a50d26c5e4eed2ca87509494ffef2d2ebd22b1eb
- https://github.com/pion/dtls
- https://pkg.go.dev/vuln/GO-2023-1534
