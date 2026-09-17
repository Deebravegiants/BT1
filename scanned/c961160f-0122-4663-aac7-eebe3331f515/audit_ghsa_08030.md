# [H] Sliver has Potential Zip Bomb Denial of Service in GzipEncoder

## Summary
Severity: High
Advisory: GHSA-2phg-qgmm-r638
CWE: CWE-409
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-2phg-qgmm-r638
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=0 <1.7.2

## Details
### Summary

GzipEncoder does not limit output size when processing compressed data. This allows unauthenticated remote attackers to crash sliver server by sending a http request with highly compressed gzip data (aka zip bomb).

### Details

In `util/encoders/gzip.go`, `Decode()` method decompresses given data by reading the entire gzip buffer at once without limiting output size.

### PoC

```python
data = gzip.compress(bytes(1024 * 1024 * 1024)) * 16
requests.post(f"http://172.17.0.2/{nonce}", data=data)
```

### Impact

Unauthenticated remote attackers can exhaust memory and cpu resource of sliver server and crash it when they have GzipEncoderID, which can be easily retrived from implant's http traffic, or by brute-forcing.

A fixed version is available at https://github.com/BishopFox/sliver/releases/tag/v1.7.2.

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-2phg-qgmm-r638
- https://github.com/BishopFox/sliver/commit/0cf5a47cfdf94b6ab481ec3ea0db09f31654c0f0
- https://github.com/BishopFox/sliver
- https://github.com/BishopFox/sliver/releases/tag/v1.7.2
- https://pkg.go.dev/vuln/GO-2026-4548
