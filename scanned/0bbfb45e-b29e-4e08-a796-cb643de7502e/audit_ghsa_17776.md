# [M] imgproxy is vulnerable to SSRF against 0.0.0.0

## Summary
Severity: Medium
Advisory: GHSA-j2hp-6m75-v4j4
CVE: CVE-2025-24354
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-27
Source: https://github.com/advisories/GHSA-j2hp-6m75-v4j4
Type: github-advisory

## Affected
- Go: `github.com/imgproxy/imgproxy` — affected >=0 <3.27.2

## Details
### Summary

Imgproxy does not block the `0.0.0.0` address, even with `IMGPROXY_ALLOW_LOOPBACK_SOURCE_ADDRESSES` set to false. This can expose services on the local host.

### Details

imgproxy protects against SSRF against a loopback address with the following check ([source](https://github.com/imgproxy/imgproxy/blob/0f37d62fd8326a32c213b30dd52e2319770885d8/security/source.go#L43C1-L47C1)):

```
if !config.AllowLoopbackSourceAddresses && ip.IsLoopback() {
	return ErrSourceAddressNotAllowed
}
```

This check is insufficient to prevent accessing services on the local host, as services may receive traffic on `0.0.0.0`. Go's `IsLoopback` ([source](https://github.com/golang/go/blob/40b3c0e58a0ae8dec4684a009bf3806769e0fc41/src/net/ip.go#L126-L131)) strictly follows the definition of loopback IPs beginning with `127`. `0.0.0.0` is not blocked.

## References
- https://github.com/imgproxy/imgproxy/security/advisories/GHSA-j2hp-6m75-v4j4
- https://nvd.nist.gov/vuln/detail/CVE-2025-24354
- https://github.com/imgproxy/imgproxy/commit/3d4fed6842aa8930ec224d0ad75b0079b858e081
- https://github.com/imgproxy/imgproxy
